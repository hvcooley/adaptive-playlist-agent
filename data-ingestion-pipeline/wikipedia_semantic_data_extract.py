import os

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
    params = {
        "action": "parse",
        "page": page_name,
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

    target_titles = set(section_titles_and_indexes.keys())
    HEADER_TAGS = {"h2", "h3", "h4"}

    sections = []
    current_title = None
    current_paragraphs = []

    for element in soup.find_all(["h2", "h3", "h4", "p"]):
        if element.name in HEADER_TAGS:
            if current_title in target_titles and current_paragraphs:
                text = "\n\n".join(current_paragraphs)
                if text.strip():
                    sections.append({"section_name": current_title, "text": text})
            headline = element.find("span", class_="mw-headline")
            current_title = headline.get_text(strip=True) if headline else element.get_text(strip=True)
            current_paragraphs = []
        elif element.name == "p" and current_title in target_titles:
            text = element.get_text(" ", strip=True)
            if text:
                current_paragraphs.append(text)

    if current_title in target_titles and current_paragraphs:
        text = "\n\n".join(current_paragraphs)
        if text.strip():
            sections.append({"section_name": current_title, "text": text})

    return sections

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
    from fetch_spotify_artists import fetch_all_artists
    TEST_ARTISTS = fetch_all_artists()
    chunks = collect_artist_corpus(TEST_ARTISTS)
    print(f"\nCollected {len(chunks)} chunks across {len(TEST_ARTISTS)} artists.")

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus_preview.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Collected {len(chunks)} chunks across {len(TEST_ARTISTS)} artists.\n\n")
        for chunk in chunks:
            f.write(f"[{chunk['metadata']['artist']} / {chunk['metadata']['section']}]\n")
            f.write(chunk["text"])
            f.write("\n\n" + "-" * 80 + "\n\n")
    print(f"Full corpus written to {output_path}")
