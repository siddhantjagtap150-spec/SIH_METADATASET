import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://standards.bis.gov.in/"

print("=" * 70)
print("BIS NEW STANDARDS PORTAL - DISCOVERY")
print("=" * 70)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

try:
    response = requests.get(BASE_URL, headers=headers, timeout=30)
    print(f"\nHTTP status: {response.status_code}")
    print(f"Downloaded bytes: {len(response.content)}")
    print(f"Final URL: {response.url}")
    response.raise_for_status()
except Exception as error:
    print("\nERROR downloading BIS portal:")
    print(error)
    raise SystemExit(1)

html = response.text
soup = BeautifulSoup(html, "html.parser")

print("\n" + "=" * 70)
print("LINKS FOUND")
print("=" * 70)

links = []
for anchor in soup.find_all("a", href=True):
    text = " ".join(anchor.get_text(" ", strip=True).split())
    href = urljoin(BASE_URL, anchor["href"])
    if text:
        links.append((text, href))

seen = set()
keywords = [
    "standard",
    "published",
    "new standard",
    "revised",
    "review",
    "download",
    "technical",
    "know your",
]

for text, href in links:
    key = (text, href)
    if key in seen:
        continue
    seen.add(key)
    if any(keyword in text.lower() or keyword in href.lower() for keyword in keywords):
        print(f"\nTEXT : {text}")
        print(f"URL  : {href}")

print("\n" + "=" * 70)
print("SCRIPTS")
print("=" * 70)

for script in soup.find_all("script", src=True):
    print(urljoin(BASE_URL, script["src"]))

print("\n" + "=" * 70)
print("FORMS")
print("=" * 70)

forms = soup.find_all("form")
print(f"Forms found: {len(forms)}")

for index, form in enumerate(forms, start=1):
    action = form.get("action", "")
    method = form.get("method", "GET")
    print(f"\nForm {index}")
    print(f"Action : {urljoin(BASE_URL, action)}")
    print(f"Method : {method}")
    for field in form.find_all(["input", "select", "textarea"]):
        name = field.get("name")
        input_type = field.get("type", field.name)
        if name:
            print(f"  {input_type}: {name}")

print("\n" + "=" * 70)
print("DISCOVERY COMPLETE")
print("=" * 70)
