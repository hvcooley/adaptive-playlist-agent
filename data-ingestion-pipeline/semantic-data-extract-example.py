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

for section in data["parse"]["sections"]:
    print(section["index"], section["line"])

#Next: Confirm that section with 'Artistry' is in the response, then query that section for the text content