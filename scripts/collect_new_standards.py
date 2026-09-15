import requests
import json
import re
from pathlib import Path

BASE = "https://standardsadmin.bis.gov.in/master-service"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json"
}

COUNT_FILE = Path("output/new_standards_department_count.txt")
OUTPUT_FILE = Path("output/new_standards_raw.json")


def load_response():
    if not COUNT_FILE.exists():
        raise FileNotFoundError(
            f"Missing file: {COUNT_FILE}"
        )

    text = COUNT_FILE.read_text(
        encoding="utf-8"
    )

    return json.loads(text)


def find_department_ids(obj):
    """
    Recursively find every value associated
    with a key containing 'departmentId'.
    """

    found = set()

    def walk(value):

        if isinstance(value, dict):

            for key, val in value.items():

                key_lower = str(key).lower()

                if (
                    "departmentid" in key_lower
                    and val is not None
                ):
                    found.add(str(val))

                walk(val)

        elif isinstance(value, list):

            for item in value:
                walk(item)

    walk(obj)

    return sorted(found)


def post(endpoint, payload):

    url = f"{BASE}/{endpoint}"

    print("\nPOST:")
    print(url)

    print("BODY:")
    print(json.dumps(
        payload,
        indent=2
    ))

    response = requests.post(
        url,
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    print("HTTP:", response.status_code)
    print("SIZE:", len(response.content))

    try:
        data = response.json()
    except Exception:
        print(response.text[:2000])
        return None

    return data


print("=" * 80)
print("BIS NEW STANDARDS COLLECTOR")
print("=" * 80)

count_data = load_response()

department_ids = find_department_ids(
    count_data
)

print("\nDEPARTMENT IDs FOUND:")
for department_id in department_ids:
    print(" -", department_id)

print(
    f"\nTOTAL DEPARTMENT IDs FOUND: "
    f"{len(department_ids)}"
)

if not department_ids:
    print(
        "\nERROR: No department IDs found."
    )
    print(
        "\nRaw response:"
    )
    print(
        json.dumps(
            count_data,
            indent=2
        )[:10000]
    )
    raise SystemExit(1)


all_results = []

for index, department_id in enumerate(
    department_ids,
    start=1
):

    print("\n" + "=" * 80)

    print(
        f"DEPARTMENT {index}/"
        f"{len(department_ids)}"
    )

    print(
        f"departmentId = {department_id}"
    )

    print("=" * 80)

    payload = {
        "departmentId": department_id
    }

    data = post(
        "getNewStandardsList",
        payload
    )

    if data is None:
        continue

    all_results.append({
        "departmentId": department_id,
        "response": data
    })


OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

output = {
    "source": "Bureau of Indian Standards",
    "endpoint": (
        f"{BASE}/getNewStandardsList"
    ),
    "total_departments": len(
        department_ids
    ),
    "departments": all_results
}

OUTPUT_FILE.write_text(
    json.dumps(
        output,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

print("\n" + "=" * 80)
print("COLLECTION COMPLETE")
print("=" * 80)

print(
    f"\nDepartments attempted: "
    f"{len(department_ids)}"
)

print(
    f"Raw output saved to:\n"
    f"{OUTPUT_FILE}"
)
