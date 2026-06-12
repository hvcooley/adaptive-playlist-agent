import os
import sys
import time

import requests
from dotenv import load_dotenv

_PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "backend"))
from genres import genres as ALL_GENRES


def _get_token(client_id: str, client_secret: str) -> str:
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _search_artists_for_genre(
    token: str,
    genre: str,
    min_popularity: int,
    pages: int,
    page_size: int,
) -> dict[str, dict]:
    """Returns {artist_id: {name, popularity}} for one genre."""
    results: dict[str, dict] = {}
    headers = {"Authorization": f"Bearer {token}"}

    for page in range(pages):
        params = {
            "q": f"genre:{genre}",
            "type": "artist",
            "limit": page_size,
            "offset": page * page_size,
        }
        response = requests.get(
            "https://api.spotify.com/v1/search",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

        items = data.get("artists", {}).get("items") or []
        for artist in items:
            if artist and artist.get("popularity", 0) >= min_popularity:
                results[artist["id"]] = {
                    "name": artist["name"],
                    "popularity": artist["popularity"],
                }

        if not data.get("artists", {}).get("next"):
            break

        time.sleep(0.1)

    return results


def fetch_all_artists(
    genres: list[str] | None = None,
    min_popularity: int = 50,
    target_count: int = 750,
    pages_per_genre: int = 4,
    page_size: int = 50,
) -> list[str]:
    """
    Fetches artist names from Spotify across the given genres.

    Uses Client Credentials auth — requires SPOTIFY_CLIENT_ID and
    SPOTIFY_CLIENT_SECRET in the environment or .env file.

    Args:
        genres: Genre list to search. Defaults to ALL_GENRES from genres.py.
        min_popularity: Spotify popularity score cutoff (0–100). 50 filters
            for artists with meaningful mainstream presence (~300K+ listeners).
        target_count: Stop collecting after this many unique artists.
        pages_per_genre: Number of paginated requests per genre (page_size results each).
        page_size: Results per API request (max 50).

    Returns:
        Artist names deduplicated and sorted by popularity descending, with
        spaces replaced by underscores for use as Wikipedia page titles.
    """
    load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))
    client_id = os.environ["SPOTIFY_CLIENT_ID"]
    client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
    token = _get_token(client_id, client_secret)

    if genres is None:
        genres = list(dict.fromkeys(ALL_GENRES))  # deduplicate while preserving order

    all_artists: dict[str, dict] = {}

    for genre in genres:
        if len(all_artists) >= target_count:
            break
        print(f"Fetching: {genre!r}")
        try:
            found = _search_artists_for_genre(
                token, genre, min_popularity, pages_per_genre, page_size
            )
            new = {k: v for k, v in found.items() if k not in all_artists}
            all_artists.update(new)
            print(f"  +{len(new)} new  (total: {len(all_artists)})")
        except requests.HTTPError as exc:
            print(f"  [SKIP] {genre!r} — {exc}", file=sys.stderr)

    sorted_artists = sorted(
        all_artists.values(), key=lambda a: a["popularity"], reverse=True
    )
    return [
        a["name"].replace(" ", "_") for a in sorted_artists[:target_count]
    ]


if __name__ == "__main__":
    artists = fetch_all_artists()
    print(f"\nFetched {len(artists)} artists.")
    for name in artists[:10]:
        print(f"  {name}")
