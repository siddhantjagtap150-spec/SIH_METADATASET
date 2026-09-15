"""Collect raw BIS standard detail and related responses for a validation batch."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "output" / "all_new_standards_raw.json"
DETAIL_DIR = PROJECT_ROOT / "output" / "raw_standard_details"
RELATED_DIR = PROJECT_ROOT / "output" / "raw_standard_related"
FAILURE_FILE = PROJECT_ROOT / "output" / "standard_enrichment_failures.json"
PROGRESS_FILE = PROJECT_ROOT / "output" / "standard_enrichment_progress.json"
REPORT_FILE = PROJECT_ROOT / "output" / "standard_enrichment_report.txt"
TEST_REPORT_FILE = PROJECT_ROOT / "output" / "standard_enrichment_test_report.txt"

PROPOSAL_BASE = "https://standardsadmin.bis.gov.in/proposal-service/"
REVIEW_BASE = "https://standardsadmin.bis.gov.in/review-service"
PRIMARY_ENDPOINT = f"{PROPOSAL_BASE}/getStandardsWithDeptAndCommittee"
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3
PER_PAGE = 100
REQUEST_DELAY = 0.3
VALIDATION_LIMIT = 5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
}

RELATED_ENDPOINTS = {
    "website_standard_details": {
        "url": f"{REVIEW_BASE}/getWebsiteStandardDetails",
        "payload": lambda identifier: {"encId": identifier, "fromPage": "guestUserPage"},
        "paginated": False,
    },
    "cross_reference": {
        "url": f"{REVIEW_BASE}/getCrossRefDetails",
        "payload": lambda identifier: {"encId": identifier, "fromPage": "guestUserPage"},
        "paginated": False,
    },
    "review_lifecycle": {
        "url": f"{REVIEW_BASE}/getWebsiteReviewLifeCycleList",
        "payload": lambda identifier: {"standardId": identifier, "fromPage": "guestUserPage"},
        "paginated": False,
    },
    "amendments": {
        "url": f"{REVIEW_BASE}/getAmendmentDetails",
        "payload": lambda identifier: {"standardId": identifier},
        "paginated": False,
    },
    "gazette": {
        "url": f"{REVIEW_BASE}/getGazettedetails",
        "payload": lambda identifier: {"standardId": identifier},
        "paginated": False,
    },
    "licence": {
        "url": f"{REVIEW_BASE}/getStandardLicenseDetails",
        "payload": lambda identifier: {
            "standardId": identifier,
            "status": "",
            "page": 1,
            "limit": PER_PAGE,
            "searchText": "",
        },
        "paginated": True,
    },
    "crs": {
        "url": f"{REVIEW_BASE}/getStandardCRSDetails",
        "payload": lambda identifier: {
            "standardId": identifier,
            "status": "",
            "page": 1,
            "limit": PER_PAGE,
            "searchText": "",
        },
        "paginated": True,
    },
    "mcs": {
        "url": f"{REVIEW_BASE}/getStandardMCSDetails",
        "payload": lambda identifier: {
            "standardId": identifier,
            "page": 1,
            "limit": PER_PAGE,
            "searchText": "",
        },
        "paginated": True,
    },
    "laboratory": {
        "url": f"{REVIEW_BASE}/getStandardLaboratoryDetails",
        "payload": lambda identifier: {
            "standardId": identifier,
            "page": 1,
            "limit": PER_PAGE,
            "searchText": "",
        },
        "paginated": True,
    },
    "product_manual": {
        "url": f"{REVIEW_BASE}/getProductManualDetails",
        "payload": lambda identifier: {"standardId": identifier},
        "paginated": False,
    },
    "corrigendum": {
        "url": f"{REVIEW_BASE}/getCorrigendumDetails",
        "payload": lambda identifier: {"standardId": identifier},
        "paginated": False,
    },
    "summary": {
        "url": f"{REVIEW_BASE}/getSummaryDetails",
        "payload": lambda identifier: {"standardId": identifier},
        "paginated": False,
    },
    "format_documents": {
        "url": f"{REVIEW_BASE}/getStandardFormatDocumentDetails",
        "payload": lambda identifier: {"standardId": identifier},
        "paginated": False,
    },
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def response_is_success(value: Any) -> bool:
    return isinstance(value, dict) and value.get("status") == "SUCCESS"


def load_records() -> list[dict]:
    dataset = read_json(INPUT_FILE)
    return [
        record
        for department in dataset.get("departments", [])
        for record in department.get("records", [])
    ]


def load_failures() -> list[dict]:
    if not FAILURE_FILE.exists():
        return []
    value = read_json(FAILURE_FILE)
    return value if isinstance(value, list) else []


def save_failure(failure: dict) -> None:
    failures = load_failures()
    failures.append(failure)
    write_json(FAILURE_FILE, failures)


def request_json(
    session: requests.Session,
    endpoint: str,
    payload: dict,
    standard_id: int,
    identifier: str | int,
) -> tuple[int, dict]:
    last_error: str | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.post(
                endpoint,
                headers=HEADERS,
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            print(
                f"standardId={standard_id} endpoint={endpoint.rsplit('/', 1)[-1]} "
                f"attempt={attempt}/{MAX_RETRIES} HTTP={response.status_code}"
            )
            data = response.json()
            if response.status_code >= 400:
                raise RuntimeError(f"HTTP {response.status_code}: {data}")
            if not isinstance(data, dict):
                raise RuntimeError("Response JSON was not an object")
            return response.status_code, data
        except (requests.RequestException, ValueError, RuntimeError) as error:
            last_error = str(error)
            if attempt < MAX_RETRIES:
                time.sleep(REQUEST_DELAY * attempt)
    raise RuntimeError(
        f"standardId={standard_id}, identifier={identifier!r}, "
        f"endpoint={endpoint}, error={last_error}"
    )


def save_related_page(
    related_dir: Path,
    filename: str,
    page: int | None,
    response: dict,
) -> Path:
    if page is None:
        path = related_dir / f"{filename}.json"
    elif page == 1:
        path = related_dir / f"{filename}.json"
    else:
        path = related_dir / f"{filename}.page-{page:03d}.json"
    write_json(path, response)
    return path


def existing_success(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        value = read_json(path)
    except (OSError, ValueError):
        return None
    return value if response_is_success(value) else None


def pagination_last_page(response: dict) -> int:
    pagination = response.get("pagination")
    if not isinstance(pagination, dict):
        return 1
    return int(pagination.get("totalPages", pagination.get("last_page", 1)) or 1)


def records_in_response(response: dict) -> int:
    data = response.get("data")
    return len(data) if isinstance(data, list) else 0


def collect_related(
    session: requests.Session,
    standard_id: int,
    standard_identifier: str,
    related_dir: Path,
    name: str,
    spec: dict,
    failures_for_standard: list[dict],
) -> dict:
    first_path = related_dir / f"{name}.json"
    first_response = existing_success(first_path)
    pages = 0
    records = 0
    if first_response is not None:
        response = first_response
        pages = 1
        records += records_in_response(response)
    else:
        payload = spec["payload"](standard_identifier)
        try:
            _, response = request_json(
                session, spec["url"], payload, standard_id, standard_identifier
            )
            save_related_page(related_dir, name, 1 if spec["paginated"] else None, response)
            pages = 1
            records += records_in_response(response)
            time.sleep(REQUEST_DELAY)
        except Exception as error:
            failure = {
                "standardId": standard_id,
                "standardEncId": standard_identifier,
                "endpoint": spec["url"],
                "payload": payload,
                "HTTP status": None,
                "response/error": str(error),
                "attempt count": MAX_RETRIES,
            }
            failures_for_standard.append(failure)
            save_failure(failure)
            return {"success": False, "pages": pages, "records": records}

    if spec["paginated"]:
        last_page = pagination_last_page(response)
        for page in range(2, last_page + 1):
            page_path = related_dir / f"{name}.page-{page:03d}.json"
            page_response = existing_success(page_path)
            if page_response is None:
                payload = spec["payload"](standard_identifier)
                payload["page"] = page
                try:
                    _, page_response = request_json(
                        session, spec["url"], payload, standard_id, standard_identifier
                    )
                    save_related_page(related_dir, name, page, page_response)
                    time.sleep(REQUEST_DELAY)
                except Exception as error:
                    failure = {
                        "standardId": standard_id,
                        "standardEncId": standard_identifier,
                        "endpoint": spec["url"],
                        "payload": payload,
                        "HTTP status": None,
                        "response/error": str(error),
                        "attempt count": MAX_RETRIES,
                    }
                    failures_for_standard.append(failure)
                    save_failure(failure)
                    return {"success": False, "pages": pages, "records": records}
            pages += 1
            records += records_in_response(page_response)

    return {"success": True, "pages": pages, "records": records}


def update_progress(progress: dict) -> None:
    progress["last update time"] = now()
    write_json(PROGRESS_FILE, progress)


def make_test_report(results: list[dict]) -> str:
    lines = [
        "BIS STANDARD ENRICHMENT VALIDATION REPORT",
        "===========================================",
        "",
        "Validation batch size: 5",
        "The collector was intentionally stopped after the first five standards.",
        "",
    ]
    for result in results:
        lines.extend([
            f"standardId: {result['standardId']}",
            f"standardNumber: {result['standardNumber']}",
            f"primary detail success: {result['primary_success']}",
            f"standardEncId present: {result['standardEncId_present']}",
        ])
        for name, detail in result["related"].items():
            lines.append(
                f"{name}: success={detail['success']}, pages={detail['pages']}, records={detail['records']}"
            )
        lines.append("raw files created:")
        lines.extend(f"- {path}" for path in result["files"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    records = load_records()
    selected = records[:VALIDATION_LIMIT]
    progress = {
        "total standards": len(records),
        "validation limit": VALIDATION_LIMIT,
        "completed primary details": 0,
        "completed related endpoint calls": 0,
        "failed primary details": 0,
        "failed related calls": 0,
        "last processed standardId": None,
        "start time": now(),
        "last update time": now(),
    }
    write_json(PROGRESS_FILE, progress)
    results = []

    with requests.Session() as session:
        for record in selected:
            standard_id = int(record["standardId"])
            standard_number = record.get("standardNumber")
            detail_path = DETAIL_DIR / f"{standard_id}.json"
            result = {
                "standardId": standard_id,
                "standardNumber": standard_number,
                "primary_success": False,
                "standardEncId_present": False,
                "related": {},
                "files": [],
            }
            primary = existing_success(detail_path)
            if primary is None:
                try:
                    _, primary = request_json(
                        session,
                        PRIMARY_ENDPOINT,
                        {"StandardId": standard_id},
                        standard_id,
                        standard_id,
                    )
                    write_json(detail_path, primary)
                    time.sleep(REQUEST_DELAY)
                except Exception as error:
                    progress["failed primary details"] += 1
                    save_failure({
                        "standardId": standard_id,
                        "endpoint": PRIMARY_ENDPOINT,
                        "payload": {"StandardId": standard_id},
                        "HTTP status": None,
                        "response/error": str(error),
                        "attempt count": MAX_RETRIES,
                    })
                    result["files"].append(str(detail_path.relative_to(PROJECT_ROOT)))
                    results.append(result)
                    progress["last processed standardId"] = standard_id
                    update_progress(progress)
                    continue
            result["primary_success"] = response_is_success(primary) and bool(primary.get("data"))
            result["files"].append(str(detail_path.relative_to(PROJECT_ROOT)))
            if result["primary_success"]:
                progress["completed primary details"] += 1
                detail = primary["data"][0]
                standard_identifier = detail.get("standardEncId")
                result["standardEncId_present"] = bool(standard_identifier)
                if standard_identifier:
                    related_dir = RELATED_DIR / str(standard_id)
                    for name, spec in RELATED_ENDPOINTS.items():
                        related_result = collect_related(
                            session,
                            standard_id,
                            standard_identifier,
                            related_dir,
                            name,
                            spec,
                            [],
                        )
                        result["related"][name] = related_result
                        if related_result["success"]:
                            progress["completed related endpoint calls"] += 1
                        else:
                            progress["failed related calls"] += 1
                        if related_dir.exists():
                            result["files"].extend(
                                str(path.relative_to(PROJECT_ROOT))
                                for path in sorted(related_dir.glob(f"{name}*.json"))
                                if str(path.relative_to(PROJECT_ROOT)) not in result["files"]
                            )
                else:
                    progress["failed related calls"] += len(RELATED_ENDPOINTS)
            else:
                progress["failed primary details"] += 1
                save_failure({
                    "standardId": standard_id,
                    "endpoint": PRIMARY_ENDPOINT,
                    "payload": {"StandardId": standard_id},
                    "HTTP status": primary.get("statusCode") if isinstance(primary, dict) else None,
                    "response/error": primary,
                    "attempt count": 1,
                })
            results.append(result)
            progress["last processed standardId"] = standard_id
            update_progress(progress)

    TEST_REPORT_FILE.write_text(make_test_report(results), encoding="utf-8")
    REPORT_FILE.write_text(
        "BIS STANDARD ENRICHMENT REPORT\n"
        "==============================\n\n"
        f"Total input standards: {len(records)}\n"
        f"Validation standards processed: {len(selected)}\n"
        f"Primary details successful: {progress['completed primary details']}\n"
        f"Primary details failed: {progress['failed primary details']}\n"
        f"Related endpoint calls successful: {progress['completed related endpoint calls']}\n"
        f"Related endpoint calls failed: {progress['failed related calls']}\n"
        "Collection stopped after the five-standard validation batch.\n",
        encoding="utf-8",
    )
    print(f"Validation report saved to: {TEST_REPORT_FILE}")
    print("STOPPED after first five standards; remaining standards were not processed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
