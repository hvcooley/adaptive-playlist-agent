import requests
import BeautifulSoup

def fetch_musical_vibe_section_labels(page_name: str) -> list[str]:
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


def collect_semantic_text_Data(page_name: str, section_titles_and_indexes: dict[str][str]) -> str:
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

        response = requests.get("https://en.wikipedia.org/w/api.php", params=params)

        html = response.json()["parse"]["text"]

        # Step 3: Extract plain text
        soup = BeautifulSoup(html, "html.parser")

        text = "\n\n".join(
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
        )
        all_semantic_text = all_semantic_text + text

if __name__ == "__main__":
    print(fetch_musical_vibe_section_labels("Blink-182"))
