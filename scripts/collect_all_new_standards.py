"""Collect every page of BIS new standards metadata."""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from datetime import date
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://standardsadmin.bis.gov.in/master-service"
COUNT_FILE = PROJECT_ROOT / "output" / "new_standards_department_count.txt"
OUTPUT_FILE = PROJECT_ROOT / "output" / "new_standards_all.json"
REPORT_FILE = PROJECT_ROOT / "output" / "all_new_standards_collection_report.txt"
OUTPUT_FILE = PROJECT_ROOT / "output" / "all_new_standards_raw.json"
PAGE_SIZE = 100
MAX_RETRIES = 3
REQUEST_DELAY_SECONDS = 0.25
TIMEOUT_SECONDS = 60
EXPECTED_DEPARTMENT_COUNT = 18
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
}


def load_department_ids() -> tuple[list[int], int]:
    """Load department IDs and the earlier department-count total."""
    if not COUNT_FILE.exists():
        raise FileNotFoundError(f"Missing file: {COUNT_FILE}")

    payload = json.loads(COUNT_FILE.read_text(encoding="utf-8"))
    department_ids = {
        int(item["departmentId"])
        for item in payload.get("data", [])
        if item.get("departmentId") is not None
    }
    earlier_total = sum(
        int(item["totalStandards"])
        for item in payload.get("data", [])
        if item.get("totalStandards") is not None
    )
    return sorted(department_ids), earlier_total


def request_page(
    session: requests.Session,
    department_id: int,
    page: int,
) -> dict:
    """Request one page, retrying failed requests up to three times."""
    payload = {"departmentId": department_id, "page": page, "per_page": PAGE_SIZE}
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.post(
                f"{BASE_URL}/getNewStandardsList",
                headers=HEADERS,
                json=payload,
                timeout=TIMEOUT_SECONDS,
            )
            print(f"departmentId={department_id} page={page} attempt={attempt}/{MAX_RETRIES} HTTP={response.status_code}")
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "SUCCESS":
                raise RuntimeError(f"API status {data.get('status')!r}: {data.get('msg')}")
            return data
        except (requests.RequestException, ValueError, RuntimeError) as error:
            last_error = error
            print(f"  request failed: {error}")
            if attempt < MAX_RETRIES:
                time.sleep(REQUEST_DELAY_SECONDS * attempt)
    raise RuntimeError(f"departmentId={department_id}, page={page} failed after {MAX_RETRIES} attempts: {last_error}")


def collect_department(
    session: requests.Session,
    department_id: int,
) -> list[dict]:
    """Collect all pages for one department and validate coverage."""
    first_response = request_page(session, department_id, page=1)
    pagination = first_response.get("pagination", {})
    reported_total = int(pagination["total"])
    last_page = int(pagination["last_page"])
    records = list(first_response.get("data", []))
    pages_collected = {int(pagination["current_page"])}
    if pages_collected != {1}:
        raise RuntimeError(f"departmentId={department_id} returned an unexpected first page")

    for page in range(2, last_page + 1):
        page_response = request_page(session, department_id, page)
        page_pagination = page_response["pagination"]
        if int(page_pagination["current_page"]) != page:
            raise RuntimeError(f"departmentId={department_id} returned the wrong page")
        if int(page_pagination["last_page"]) != last_page:
            raise RuntimeError(f"departmentId={department_id} changed last_page during collection")
        records.extend(page_response.get("data", []))
        pages_collected.add(page)
        time.sleep(REQUEST_DELAY_SECONDS)

    expected_pages = set(range(1, last_page + 1))
    if pages_collected != expected_pages:
        raise RuntimeError(f"departmentId={department_id} skipped a page")
    return {
        "departmentId": department_id,
        "reported_total": reported_total,
        "last_page": last_page,
        "records_collected": len(records),
        "pages_collected": len(pages_collected),
        "records": records,
    }


def duplicate_values(records: list[dict], field: str) -> list[object]:
    """Return duplicate non-empty values for a raw record field."""
    counts = Counter(record[field] for record in records if record.get(field) not in (None, ""))
    return sorted(value for value, count in counts.items() if count > 1)


def build_report(departments: list[dict], earlier_total: int | None, failure: str | None = None) -> str:
    """Build the required collection report."""
    records = [record for department in departments for record in department["records"]]
    reported_total = sum(department["reported_total"] for department in departments)
    unique_ids = {record["standardId"] for record in records if record.get("standardId") not in (None, "")}
    unique_numbers = {record["standardNumber"] for record in records if record.get("standardNumber") not in (None, "")}
    lines = [
        "BIS NEW STANDARDS COLLECTION REPORT",
        "====================================",
        "",
        "Departments:", str(EXPECTED_DEPARTMENT_COUNT),
        "", "Configured page size:", str(PAGE_SIZE),
        "", "For each department:",
    ]
    for department in departments:
        lines.extend([
            "", f"departmentId: {department['departmentId']}",
            f"reported total: {department['reported_total']}",
            f"last page: {department['last_page']}",
            f"pages collected: {department['pages_collected']}",
            f"records collected: {department['records_collected']}",
        ])
    lines.extend([
        "", "Total reported records: " + str(reported_total),
        "Total records collected: " + str(len(records)),
        "Unique standard IDs: " + str(len(unique_ids)),
        "Unique standard numbers: " + str(len(unique_numbers)),
        "Duplicate standard IDs: " + json.dumps(duplicate_values(records, "standardId")),
        "Duplicate standard numbers: " + json.dumps(duplicate_values(records, "standardNumber")),
        "", "Earlier department-count endpoint total (if available): " + str(earlier_total),
        "Sum of pagination totals from getNewStandardsList: " + str(reported_total),
        "Actual records collected: " + str(len(records)),
    ])
    if earlier_total != reported_total or reported_total != len(records):
        lines.append("Discrepancy: reported totals and/or collected records differ; no discrepancy was resolved by guessing.")
    else:
        lines.append("Discrepancy: none.")
    if failure:
        lines.extend(["", "COLLECTION FAILED:", failure])
    else:
        lines.extend(["", "Validation: every department completed successfully.", "Every department reached its reported last_page.", "Collected count matches the sum of records returned.", "No page was silently skipped."])
    return "\n".join(lines) + "\n"


def main() -> int:
    """Collect all BIS new-standard pages into a separate raw output file."""
    department_ids, earlier_total = load_department_ids()
    departments = []
    failure = None

    if len(department_ids) != EXPECTED_DEPARTMENT_COUNT:
        failure = f"Expected {EXPECTED_DEPARTMENT_COUNT} department IDs, found {len(department_ids)}"
    else:
        with requests.Session() as session:
            for department_id in department_ids:
                try:
                    departments.append(collect_department(session, department_id))
                except RuntimeError as error:
                    failure = str(error)
                    print(f"COLLECTION FAILED: {failure}")
                    break

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(build_report(departments, earlier_total, failure), encoding="utf-8")
    print(f"Report saved to: {REPORT_FILE}")
    if failure:
        return 1

    records = [record for department in departments for record in department["records"]]
    output = {
        "source": {
            "organization": "Bureau of Indian Standards",
            "endpoint": f"{BASE_URL}/getNewStandardsList",
            "collection_date": str(date.today()),
            "collection_method": "official_bis_api",
        },
        "summary": {
            "department_count": EXPECTED_DEPARTMENT_COUNT,
            "configured_per_page": PAGE_SIZE,
            "records_collected": len(records),
            "unique_standard_ids": len({record["standardId"] for record in records if record.get("standardId") not in (None, "")}),
            "unique_standard_numbers": len({record["standardNumber"] for record in records if record.get("standardNumber") not in (None, "")}),
            "duplicate_standard_ids": duplicate_values(records, "standardId"),
            "duplicate_standard_numbers": duplicate_values(records, "standardNumber"),
            "department_totals": {str(item["departmentId"]): item["reported_total"] for item in departments},
            "department_records_collected": {str(item["departmentId"]): item["records_collected"] for item in departments},
        },
        "departments": departments,
    }
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Raw dataset saved to: {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
