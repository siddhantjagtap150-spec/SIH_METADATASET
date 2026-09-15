"""
BIS Standards Metadata Collector
--------------------------------

Purpose:
    Collect publicly available BIS Indian Standard metadata
    from official BIS catalogue pages.

Source policy:
    OFFICIAL BIS SOURCES ONLY

Output:
    data/standards/standards.json

Important:
    This script collects METADATA.
    It does not download or reproduce copyrighted standard PDFs.

Run:
    python scripts/collect_standards.py
"""

from __future__ import annotations

import json
import re
import time
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "standards" / "standards.json"
SOURCE_URL = "https://www.services.bis.gov.in/php/BIS_2.0/dgdashboard/Published_Standards"
TIMEOUT_SECONDS = 60
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def clean_text(value: str | None) -> str | None:
    """Normalize whitespace."""
    if value is None:
        return None
    value = re.sub(r"\s+", " ", value).strip()
    return value if value else None


def normalize_is_number(value: str | None) -> str | None:
    """Normalize common BIS IS-number formatting."""
    value = clean_text(value)
    if not value:
        return None
    value = re.sub(r"\s*:\s*", ": ", value)
    return re.sub(r"\s*/\s*", "/", value)


def make_entity_id(is_number: str | None) -> str:
    """Create a deterministic entity ID from an IS number."""
    if not is_number:
        return "STD-UNKNOWN"
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", is_number).strip("-").upper()
    return f"STD-{cleaned}"


def extract_year(value: str | None) -> int | None:
    """Extract a four-digit year."""
    if not value:
        return None
    match = re.search(r"\b(19|20)\d{2}\b", value)
    if match:
        return int(match.group())
    return None


def download_page() -> str:
    """Download the official BIS published standards page."""
    print("\nDownloading BIS page...")
    print(SOURCE_URL)
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    print("HTTP status:", response.status_code)
    print("Downloaded bytes:", len(response.content))
    response.raise_for_status()
    return response.text


def soup_from_html(html: str) -> BeautifulSoup:
    """Create a BeautifulSoup parser."""
    return BeautifulSoup(html, "html.parser")


def load_existing_dataset() -> dict:
    """Load existing standards.json without destroying collected records."""
    if not OUTPUT_FILE.exists():
        return {
            "dataset": {
                "dataset_id": "BIS-STANDARDS-MASTER",
                "dataset_name": "BIS Indian Standards Master Dataset",
                "version": "1.0.0",
                "source_authority": "Bureau of Indian Standards",
                "source_policy": "official_only",
                "last_verified": str(date.today()),
                "record_count": 0,
            },
            "records": [],
        }
    with OUTPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def discover_department_links(html: str) -> list[dict]:
    """Discover technical department links from the BIS landing page."""
    soup = soup_from_html(html)
    departments = []
    excluded = {
        "new standards",
        "revised standards",
        "know your standard",
        "group wise classification",
        "ministry/department wise classification",
    }
    for link in soup.find_all("a"):
        href = link.get("href")
        text = clean_text(link.get_text(" ", strip=True))
        if not href or not text or "dgdashboard" not in href.lower():
            continue
        if text.lower() in excluded:
            continue
        full_url = urljoin(SOURCE_URL, href)
        departments.append({"department_name": text, "url": full_url})
    unique = {department["url"]: department for department in departments}
    return list(unique.values())


IS_PATTERN = re.compile(
    r"\bIS(?:\s*/\s*(?:ISO|IEC|QC))?\s*[0-9A-Z./()\-]+\s*:\s*\d{4}",
    re.IGNORECASE,
)


def find_is_number(text: str | None) -> str | None:
    """Find and normalize an Indian Standard number in table text."""
    if not text:
        return None
    match = IS_PATTERN.search(text)
    return normalize_is_number(match.group(0)) if match else None


def parse_tables(html: str) -> list[dict]:
    """Parse all BIS HTML tables containing standard numbers."""
    soup = soup_from_html(html)
    tables = soup.find_all("table")
    print("\nHTML tables found:", len(tables))
    records = []

    for table_index, table in enumerate(tables, start=1):
        rows = table.find_all("tr")
        if not rows:
            continue
        print(f"Table {table_index}: {len(rows)} rows")
        headers = [
            clean_text(cell.get_text(" ", strip=True)).lower()
            for cell in rows[0].find_all(["th", "td"])
        ]
        headers = [header for header in headers if header]

        for row in rows:
            values = [
                clean_text(cell.get_text(" ", strip=True))
                for cell in row.find_all(["td", "th"])
            ]
            values = [value for value in values if value]
            if not values:
                continue
            is_number = find_is_number(" | ".join(values))
            if not is_number:
                continue

            title = reaffirmation = amendments = equivalence = None
            for index, header in enumerate(headers):
                if index >= len(values):
                    continue
                value = values[index]
                if "title" in header or "subject" in header:
                    title = value
                elif "reaffirm" in header:
                    reaffirmation = value
                elif "amend" in header:
                    amendments = value
                elif "eqv" in header or "equivalence" in header:
                    equivalence = value

            if not title:
                candidates = [
                    value
                    for value in values
                    if value != is_number
                    and not re.fullmatch(r"\d+", value)
                    and value.lower()
                    not in {"published standards", "is no.", "title", "s.no", "si. no."}
                ]
                if candidates:
                    title = max(candidates, key=len)

            records.append(
                build_standard_record(
                    is_number=is_number,
                    title=title,
                    department=None,
                    amendment=amendments,
                    source_url=SOURCE_URL,
                )
            )
    return records


def parse_standard_rows(html: str, department_name: str | None = None) -> list[dict]:
    """Parse standard metadata rows from a department page."""
    soup = soup_from_html(html)
    records = []
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            values = [clean_text(cell.get_text(" ", strip=True)) for cell in cells]
            values = [value for value in values if value]
            if len(values) < 2:
                continue
            joined = " | ".join(values)
            is_match = re.search(
                r"\bIS(?:/ISO|/IEC|/QC)?\s*[A-Z0-9./()-]+\s*:\s*\d{4}",
                joined,
                flags=re.IGNORECASE,
            )
            if not is_match:
                continue
            is_number = normalize_is_number(is_match.group(0))
            title = values[2] if len(values) >= 3 else values[1]
            amendment = next(
                (value for value in values[1:] if re.fullmatch(r"\d+", value or "")),
                None,
            )
            records.append(
                build_standard_record(
                    is_number=is_number,
                    title=title,
                    department=department_name,
                    amendment=amendment,
                    source_url=SOURCE_URL,
                )
            )
    return records


def build_standard_record(
    is_number: str | None,
    title: str | None,
    department: str | None,
    amendment: str | None,
    source_url: str,
) -> dict:
    """Build a metadata record compatible with the project schema."""
    today = str(date.today())
    return {
        "entity_id": make_entity_id(is_number),
        "entity_type": "standard",
        "name": title or is_number,
        "aliases": [],
        "classification": {"domain": "standards", "technical_department": department},
        "description": None,
        "purpose": None,
        "stakeholders": [],
        "industry_sectors": [],
        "products": [],
        "standards": {
            "is_number": is_number,
            "title": title,
            "revision": None,
            "reviewed_in": None,
            "superseding_standard": None,
            "degree_of_equivalence": None,
            "number_of_revisions": None,
            "number_of_amendments": int(amendment) if amendment and amendment.isdigit() else None,
            "aspect": None,
            "language": None,
            "reaffirmation_year": None,
            "technical_department": department,
            "technical_committee": None,
            "member_secretary": None,
        },
        "schemes": [],
        "qcos": [],
        "applicability": None,
        "eligibility": None,
        "requirements": [],
        "procedure": [],
        "testing": [],
        "certification_or_registration": [],
        "fees": [],
        "timeline": [],
        "validity": None,
        "renewal": [],
        "surveillance": [],
        "inspection": [],
        "complaints": [],
        "appeals_and_grievances": [],
        "location": {},
        "contacts": [],
        "related_entities": [],
        "common_questions": [],
        "keywords": [],
        "search_metadata": {
            "normalized_is_number": is_number,
            "search_text": " ".join(filter(None, [is_number, title, department])),
        },
        "source": {
            "organization": "Bureau of Indian Standards",
            "source_type": "bis_official",
            "official_url": source_url,
            "document_type": "webpage",
            "verification_status": "verified",
            "last_verified": today,
        },
        "metadata": {
            "record_status": "active",
            "data_quality": "official_metadata",
            "created_at": today,
            "updated_at": today,
        },
    }


def deduplicate_records(records: list[dict]) -> list[dict]:
    """Deduplicate records by entity ID."""
    unique = {}
    for record in records:
        entity_id = record.get("entity_id")
        if entity_id:
            unique[entity_id] = record
    return list(unique.values())


def save_dataset(dataset: dict) -> None:
    """Save the collected dataset."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    dataset["dataset"]["last_verified"] = str(date.today())
    dataset["dataset"]["record_count"] = len(dataset["records"])
    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(dataset, file, ensure_ascii=False, indent=2)


def main():
    """Collect standards from all tables on the official BIS page."""
    print("=" * 70)
    print("BIS STANDARDS COLLECTOR")
    print("VERSION 2")
    print("=" * 70)
    try:
        html = download_page()
    except Exception as error:
        print("\nFAILED TO DOWNLOAD BIS PAGE")
        print(error)
        return

    print("\nParsing BIS tables...")
    records = parse_tables(html)
    print("\nRaw records discovered:", len(records))
    records = deduplicate_records(records)
    print("Unique records discovered:", len(records))

    dataset = load_existing_dataset()
    existing = dataset.get("records", [])
    print("Existing records:", len(existing))
    merged = deduplicate_records(existing + records)
    merged.sort(key=lambda record: record.get("standards", {}).get("is_number") or "")
    dataset["records"] = merged
    save_dataset(dataset)

    print("\n" + "=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)
    print("Total unique standards:", len(merged))
    print("\nSaved to:")
    print(OUTPUT_FILE)
    if records:
        print("\nSample records:")
        for record in records[:5]:
            print("-", record["standards"]["is_number"], ":", record["name"])
    else:
        print("\nWARNING: ZERO RECORDS FOUND.")
        print("The BIS page may be loading its data dynamically.")


if __name__ == "__main__":
    main()
