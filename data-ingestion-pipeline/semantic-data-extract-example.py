import requests
from bs4 import BeautifulSoup


def fetch_musical_vibe_section_labels(page_name: str) -> list[str]:
    '''
    Experimental Function. Do not use in data pipeline
    '''
    url = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=parse"
        f"&page={requests.utils.quote(page_name)}"
        "&prop=sections"
        "&format=json"
    )

    headers = {
        "User-Agent": "adaptive-playlist-agent/1.0 (https://github.com/yourusername/adaptive-playlist-agent; contact: your-email@example.com)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(
            f"Wikipedia API request failed with status {response.status_code}: {response.text}"
        )

    data = response.json()

    sections = data["parse"]["sections"]

    artistry_index = next(
        (i for i, s in enumerate(sections) if s["line"] == "Artistry"), None
    )

    if artistry_index is None:
        raise ValueError("'Artistry' section not found in response")

    artistry_toclevel = sections[artistry_index]["toclevel"]

    section_labels = []
    for section in sections[artistry_index + 1:]:
        if section["toclevel"] <= artistry_toclevel:
            break
        section_labels.append(section["line"])

    return section_labels



def fetch_section_titles_and_indexes(page_name: str) -> dict[str, int]:
    url = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=parse"
        f"&page={requests.utils.quote(page_name)}"
        "&prop=sections"
        "&format=json"
    )

    headers = {
        "User-Agent": "adaptive-playlist-agent/1.0 (https://github.com/yourusername/adaptive-playlist-agent; contact: your-email@example.com)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(
            f"Wikipedia API request failed with status {response.status_code}: {response.text}"
        )

    sections = response.json()["parse"]["sections"]

    return {section["line"]: int(section["index"]) for section in sections}


def collect_semantic_text_data(page_name: str, section_titles_and_indexes: dict[str, int]) -> list[dict]:
    """
    Collects text data from each section of a band or artist's Wikipedia page.

    Args:
        page_name: The band or artist name that is the Wikipedia page title.
        section_titles_and_indexes: A dictionary where keys are section titles and values are section indexes.

    Returns:
        list[dict]: One dict per non-empty section with keys 'section_name' and 'text'.
    """
    sections = []
    for section_name, section_index in section_titles_and_indexes.items():
        params = {
            "action": "parse",
            "page": page_name,
            "section": section_index,
            "prop": "text",
            "formatversion": 2,
            "format": "json"
        }

        headers = {
            "User-Agent": "adaptive-playlist-agent/1.0 (https://github.com/yourusername/adaptive-playlist-agent; contact: your-email@example.com)"
        }

        response = requests.get("https://en.wikipedia.org/w/api.php", params=params, headers=headers)

        html = response.json()["parse"]["text"]
        soup = BeautifulSoup(html, "html.parser")

        text = "\n\n".join(
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
        )

        if text.strip():
            sections.append({"section_name": section_name, "text": text})

    return sections

TEST_ARTISTS = [
    "Blink-182",
    "Kings_of_Leon",
    "Kendrick_Lamar",
    "Taylor_Swift",
    "The_Beatles",
    "Daft_Punk",
    "Treaty_Oak_Revival",
    "Imagine_Dragons",
    "Tame_Impala",
    "Billie_Eilish",
]


def collect_artist_corpus(artists: list[str]) -> list[dict]:
    """
    Collects Wikipedia section text for a list of artists and returns Pinecone-ready chunks.

    Args:
        artists: List of artist or band names matching their Wikipedia page titles.

    Returns:
        list[dict]: Each dict has 'id', 'text', and 'metadata' keys ready for Pinecone upsert.
                    Artists whose pages could not be fetched are skipped and logged to stderr.
    """
    chunks: list[dict] = []

    for artist in artists:
        try:
            section_titles_and_indexes = fetch_section_titles_and_indexes(artist)
            sections = collect_semantic_text_data(artist, section_titles_and_indexes)
            for section in sections:
                chunk_id = f"{artist}__{section['section_name'].replace(' ', '_')}"
                chunks.append({
                    "id": chunk_id,
                    "text": section["text"],
                    "metadata": {"artist": artist, "section": section["section_name"]},
                })
            print(f"[OK] {artist} — {len(sections)} sections")
        except Exception as exc:
            print(f"[SKIP] {artist} — {exc}", file=__import__('sys').stderr)

    return chunks


if __name__ == "__main__":
    chunks = collect_artist_corpus(TEST_ARTISTS)
    print(f"\nCollected {len(chunks)} chunks across {len(TEST_ARTISTS)} artists.")
    for chunk in chunks[:5]:
        preview = chunk["text"][:100].replace("\n", " ")
        print(f"  [{chunk['metadata']['artist']} / {chunk['metadata']['section']}] {preview}…")
