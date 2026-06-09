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


def collect_semantic_text_data(page_name: str, section_titles_and_indexes: dict[str, int]) -> str:
    """
    Collects all the text data ideal for semantic meaning embedding from a band or artist's wikipedia page

    Args:
        page_name: The band or artist name that is the wikipedia page title.
        section_titles_and_indexes: A dictionary where keys are the section title and the value is the section title's index.
        
    Returns:
       str: A single string with all the textual data from the artist or band's wikipedia page
    """
    all_semantic_text = ""
    for section_ndx, section_name in enumerate(section_titles_and_indexes):

        params = {
            "action": "parse",
            "page": page_name,
            "section": section_ndx,
            "prop": "text",
            "formatversion": 2,
            "format": "json"
        }

        headers = {
            "User-Agent": "adaptive-playlist-agent/1.0 (https://github.com/yourusername/adaptive-playlist-agent; contact: your-email@example.com)"
        }

        response = requests.get("https://en.wikipedia.org/w/api.php", params=params, headers=headers)

        html = response.json()["parse"]["text"]

        # Step 3: Extract plain text
        soup = BeautifulSoup(html, "html.parser")

        text = "\n\n".join(
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
        )
        all_semantic_text = all_semantic_text + text
    
    return all_semantic_text

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


def collect_artist_corpus(artists: list[str]) -> dict[str, str]:
    """
    Collects all semantic text data from Wikipedia for a list of artists/bands.

    Args:
        artists: List of artist or band names matching their Wikipedia page titles.

    Returns:
        dict mapping each artist name to their combined Wikipedia text. Artists
        whose pages could not be fetched are omitted and logged to stderr.
    """
    corpus: dict[str, str] = {}

    for artist in artists:
        try:
            section_titles_and_indexes = fetch_section_titles_and_indexes(artist)
            text = collect_semantic_text_data(artist, section_titles_and_indexes)
            corpus[artist] = text
            print(f"[OK] {artist} — {len(text)} chars")
        except Exception as exc:
            print(f"[SKIP] {artist} — {exc}")

    return corpus


if __name__ == "__main__":
    corpus = collect_artist_corpus(TEST_ARTISTS)
    print(f"\nCollected data for {len(corpus)} artists.")
    for artist, text in corpus.items():
        preview = text[:120].replace("\n", " ")
        print(f"  {artist}: {preview}…")
