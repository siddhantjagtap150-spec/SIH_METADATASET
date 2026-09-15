import re
import requests
from urllib.parse import urljoin
from pathlib import Path

BASE_URL = "https://standards.bis.gov.in/"
MAIN_JS = "main.f7e76eff3af0f234.js"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}

print("=" * 80)
print("BIS PORTAL - ALL JAVASCRIPT CHUNK DISCOVERY")
print("=" * 80)

main_url = urljoin(BASE_URL, MAIN_JS)

response = requests.get(
    main_url,
    headers=headers,
    timeout=60
)

print("\nMain JS status:", response.status_code)
print("Main JS bytes:", len(response.content))
response.raise_for_status()
main_js = response.text

js_files = set()
patterns = [
    r'["\']([^"\']+\.js)["\']',
    r'([A-Za-z0-9_\-./]+\.js)'
]

for pattern in patterns:
    for match in re.findall(pattern, main_js):
        if match.endswith(".js"):
            js_files.add(match)

js_files.add(MAIN_JS)
print("\nJavaScript files discovered:", len(js_files))

resolved_js = set()
for js_file in js_files:
    if js_file.startswith(("http://", "https://")):
        url = js_file
    elif js_file.startswith("/"):
        url = "https://standards.bis.gov.in" + js_file
    else:
        url = urljoin(BASE_URL, js_file)
    resolved_js.add(url)

print("\nResolved JavaScript URLs:")
for url in sorted(resolved_js):
    print(" ", url)

downloaded = {}
for url in sorted(resolved_js):
    try:
        result = requests.get(url, headers=headers, timeout=60)
        if result.status_code == 200:
            downloaded[url] = result.text
            print(f"\nOK  {len(result.content):>9} bytes  {url}")
        else:
            print(f"\nERR {result.status_code:>3}          {url}")
    except Exception as error:
        print(f"\nERR {url}")
        print("   ", error)

api_strings = set()
standard_strings = set()
keywords = [
    "standard", "published", "revised", "review", "search",
    "classification", "isnumber", "indian", "download", "details",
    "detail", "catalog", "programme", "knowyour"
]

for url, js in downloaded.items():
    api_pattern = r'["\']([^"\']*/api/[^"\']*)["\']'
    for endpoint in re.findall(api_pattern, js, flags=re.IGNORECASE):
        api_strings.add((url, endpoint))

    string_pattern = r'["\']([^"\']{3,300})["\']'
    for value in re.findall(string_pattern, js, flags=re.IGNORECASE):
        if any(keyword in value.lower() for keyword in keywords):
            standard_strings.add((url, value))

print("\n" + "=" * 80)
print("ALL API STRINGS")
print("=" * 80)
for url, endpoint in sorted(api_strings):
    print("\nFILE:", url)
    print("API :", endpoint)

print("\n" + "=" * 80)
print("STANDARDS-RELATED STRINGS")
print("=" * 80)
for url, value in sorted(standard_strings):
    print("\nFILE:", url)
    print("STRING:", value)

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
report_file = output_dir / "bis_all_js_discovery.txt"

with report_file.open("w", encoding="utf-8") as file:
    file.write("=" * 80 + "\n")
    file.write("BIS ALL JAVASCRIPT DISCOVERY\n")
    file.write("=" * 80 + "\n\n")
    file.write(f"JavaScript files discovered: {len(js_files)}\n")
    file.write(f"JavaScript files downloaded: {len(downloaded)}\n")
    file.write(f"API strings found: {len(api_strings)}\n")
    file.write(f"Standards-related strings found: {len(standard_strings)}\n")
    file.write("\n\n" + "=" * 80 + "\n")
    file.write("ALL API STRINGS\n")
    file.write("=" * 80 + "\n")
    for url, endpoint in sorted(api_strings):
        file.write("\nFILE: " + url + "\n")
        file.write("API : " + endpoint + "\n")
    file.write("\n\n" + "=" * 80 + "\n")
    file.write("STANDARDS-RELATED STRINGS\n")
    file.write("=" * 80 + "\n")
    for url, value in sorted(standard_strings):
        file.write("\nFILE: " + url + "\n")
        file.write("STRING: " + value + "\n")

print("\n" + "=" * 80)
print("DISCOVERY COMPLETE")
print("=" * 80)
print("\nReport:")
print(report_file)
report.append("JAVASCRIPT CONTEXT")
report.append("=" * 80)

for endpoint in interesting:
    position = js.lower().find(endpoint.lower())
    if position == -1:
        continue
    start = max(0, position - 1500)
    end = min(len(js), position + len(endpoint) + 2500)
    report.append("")
    report.append("-" * 80)
    report.append("ENDPOINT")
    report.append("-" * 80)
    report.append(endpoint)
    report.append("")
    report.append("CONTEXT")
    report.append("-" * 80)
    report.append(js[start:end])

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)

print("")
print("=" * 80)
print("DISCOVERY COMPLETE")
print("=" * 80)
print("\nFull report saved to:")
print(OUTPUT_FILE)
print("\nImportant:")
print("Open output/bis_api_discovery.txt and send me its contents.")
