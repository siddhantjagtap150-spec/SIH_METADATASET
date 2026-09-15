import re
import requests
from urllib.parse import urljoin

BASE_URL = "https://standards.bis.gov.in/"

JS_FILES = [
    "runtime.80a097032193d463.js",
    "polyfills.55d4c5f200113cc4.js",
    "main.f7e76eff3af0f234.js"
]

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}

print("=" * 80)
print("BIS ANGULAR LAZY CHUNK DISCOVERY")
print("=" * 80)

all_js = {}

for filename in JS_FILES:
    url = urljoin(BASE_URL, filename)
    response = requests.get(url, headers=headers, timeout=60)
    print(f"\n{filename} -> HTTP {response.status_code}, {len(response.content)} bytes")
    if response.status_code == 200:
        all_js[filename] = response.text

print("\n" + "=" * 80)
print("JAVASCRIPT CHUNK REFERENCES")
print("=" * 80)

chunk_names = set()

for js in all_js.values():
    for match in re.findall(r'["\']([^"\']+\.js)["\']', js):
        chunk_names.add(match)
    for match in re.findall(r'([A-Za-z0-9_\-./]+\.js)', js):
        chunk_names.add(match)

for chunk in sorted(chunk_names):
    print(chunk)

print(f"\nTOTAL JS REFERENCES FOUND: {len(chunk_names)}")

print("\n" + "=" * 80)
print("LAZY-LOAD / CHUNK CONTEXT")
print("=" * 80)

keywords = ["chunk", "lazy", "loadChildren", "import(", "standards", "standard"]

for filename, js in all_js.items():
    lower = js.lower()
    for keyword in keywords:
        positions = []
        start = 0
        while True:
            position = lower.find(keyword.lower(), start)
            if position == -1:
                break
            positions.append(position)
            start = position + 1
            if len(positions) >= 10:
                break
        for position in positions:
            print("\n")
            print("-" * 80)
            print(f"FILE: {filename} | KEYWORD: {keyword}")
            print("-" * 80)
            print(js[max(0, position - 500):min(len(js), position + 1000)])

print("\n" + "=" * 80)
print("BIS BACKEND REFERENCES")
print("=" * 80)

backend_keywords = [
    "standardsadmin.bis.gov.in",
    "standardsmodule.bis.gov.in",
    "guest.bis.gov.in"
]

for filename, js in all_js.items():
    for keyword in backend_keywords:
        start = 0
        while True:
            position = js.lower().find(keyword.lower(), start)
            if position == -1:
                break
            print("\n")
            print("-" * 80)
            print(f"FILE: {filename} | BACKEND: {keyword}")
            print("-" * 80)
            print(js[max(0, position - 1500):min(len(js), position + 2500)])
            start = position + len(keyword)

print("\n" + "=" * 80)
print("DISCOVERY COMPLETE")
print("=" * 80)
