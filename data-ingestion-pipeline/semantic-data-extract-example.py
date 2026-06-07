import requests

url = (
    "https://en.wikipedia.org/w/api.php"
    "?action=parse"
    "&page=Blink-182"
    "&prop=sections"
    "&format=json"
)

response = requests.get(url)
data = response.json()

for section in data["parse"]["sections"]:
    print(section["index"], section["line"])