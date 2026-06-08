import requests

url = (
    "https://en.wikipedia.org/w/api.php"
    "?action=parse"
    "&page=Blink-182"
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

section_labels_with_semantic_text = []
for section in sections[artistry_index + 1:]:
    if section["toclevel"] <= artistry_toclevel:
        break
    section_labels_with_semantic_text.append(section["line"])

print(section_labels_with_semantic_text)
