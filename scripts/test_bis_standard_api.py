import requests
import json

URL = "https://standardsadmin.bis.gov.in/master-service/getNewStandardsList"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json"
}

print("=" * 80)
print("BIS NEW STANDARDS API TEST")
print("=" * 80)

print("\nURL:")
print(URL)

try:
    response = requests.post(
        URL,
        headers=headers,
        json={},
        timeout=60
    )

    print("\nHTTP STATUS:")
    print(response.status_code)

    print("\nCONTENT TYPE:")
    print(response.headers.get("Content-Type"))

    print("\nRESPONSE SIZE:")
    print(len(response.content), "bytes")

    print("\nRESPONSE:")
    print(response.text[:5000])

    with open(
        "output/new_standards_response.txt",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(response.text)

except Exception as error:
    print("\nERROR:")
    print(repr(error))

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
