import requests
import json

BASE = "https://standardsadmin.bis.gov.in/master-service"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json"
}


def test_endpoint(name, payload):
    url = f"{BASE}/{name}"

    print("\n" + "=" * 80)
    print(name)
    print("=" * 80)

    print("URL:")
    print(url)

    print("\nREQUEST BODY:")
    print(json.dumps(payload, indent=2))

    try:
        r = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )

        print("\nHTTP STATUS:")
        print(r.status_code)

        print("\nCONTENT TYPE:")
        print(r.headers.get("Content-Type"))

        print("\nRESPONSE SIZE:")
        print(len(r.content), "bytes")

        print("\nRESPONSE:")
        print(r.text[:10000])

        return r.text

    except Exception as e:
        print("\nERROR:")
        print(repr(e))
        return None


response = test_endpoint(
    "getNewStandardsDepartmentCount",
    {}
)

if response:
    with open(
        "output/new_standards_department_count.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(response)


response = test_endpoint(
    "getNewStandardsCommitteeCount",
    {}
)

if response:
    with open(
        "output/new_standards_committee_count.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(response)


print("\n" + "=" * 80)
print("DISCOVERY COMPLETE")
print("=" * 80)
