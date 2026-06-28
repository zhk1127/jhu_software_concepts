"""Scrape GradCafe applicant records for incremental worker ingestion."""

import json
import time
import html as html_lib
from urllib.parse import urlencode

import urllib3
from bs4 import BeautifulSoup


BASE_URL = "https://www.thegradcafe.com/survey"
RESULT_BASE_URL = "https://www.thegradcafe.com/result/"
OUTPUT_FILE = "applicant_data.json"

TARGET_RECORDS = 35000
DELAY_SECONDS = 1.0
MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 10

http = urllib3.PoolManager()


def build_url(page=1):
    """Build the GradCafe results URL for a page number."""
    params = {
        "page": page,
        "sort": "newest",
    }
    return BASE_URL + "?" + urlencode(params)


def fetch_page(page=1):
    """Fetch a GradCafe HTML page."""
    url = build_url(page)

    response = http.request(
        "GET",
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (JHU Software Concepts student scraper)"
        },
    )

    if response.status != 200:
        raise RuntimeError(f"Request failed with status {response.status}: {url}")

    return response.data.decode("utf-8", errors="replace")


def fetch_page_with_retries(page=1):
    """Fetch a page with retry handling for transient failures."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return fetch_page(page)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Page {page} failed attempt {attempt}/{MAX_RETRIES}: {e}")

            if attempt < MAX_RETRIES:
                print(f"Waiting {RETRY_WAIT_SECONDS} seconds before retry...")
                time.sleep(RETRY_WAIT_SECONDS)

    print(f"Skipping page {page} after {MAX_RETRIES} failed attempts.")
    return None


def extract_results_from_html(html_text):
    """Extract applicant result records from GradCafe HTML."""
    soup = BeautifulSoup(html_text, "html.parser")
    app_div = soup.find("div", id="app")

    if app_div is None:
        raise ValueError("Could not find div with id='app'.")

    data_page = app_div.get("data-page")

    if not data_page:
        raise ValueError("Could not find data-page attribute.")

    decoded = html_lib.unescape(data_page)
    data = json.loads(decoded)

    return data["props"]["results"]


def clean_record(record):
    """Convert a scraped HTML record into a normalized dictionary."""
    result_id = record.get("id")

    return {
        "program": record.get("program"),
        "university": record.get("school"),
        "comments": record.get("notes"),
        "date_added": record.get("added_on_label"),
        "url": f"{RESULT_BASE_URL}{result_id}" if result_id else None,
        "status": record.get("decision"),
        "acceptance_date": record.get("acceptedDate"),
        "rejection_date": record.get("rejectedDate"),
        "waitlist_date": record.get("waitlistedDate"),
        "interview_date": record.get("interviewDate"),
        "term": record.get("season"),
        "US/International": record.get("status"),
        "GRE Score": record.get("greq"),
        "GRE V Score": record.get("grev"),
        "Degree": record.get("level"),
        "GPA": record.get("ugpa"),
        "GRE AW": record.get("grew"),
        "raw_record": record,
    }


def save_data(data, filename=OUTPUT_FILE):
    """Save scraped applicant records to disk as JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_data(filename=OUTPUT_FILE):
    """Load scraped applicant records from disk."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def _deduplicate_by_url(input_records):
    """Remove duplicate records using the applicant URL."""
    seen = set()
    unique_records = []

    for record in input_records:
        url = record.get("url")

        if url in seen:
            continue

        seen.add(url)
        unique_records.append(record)

    return unique_records


def scrape_data(target_records=TARGET_RECORDS):
    """Scrape applicant records across GradCafe result pages."""
    all_records = load_data()
    all_records = _deduplicate_by_url(all_records)

    page = len(all_records) // 20 + 1
    last_page = None

    print(f"Starting with {len(all_records)} existing records.")
    print(f"Starting from page {page}.")

    while len(all_records) < target_records:
        print(f"Fetching page {page}...")

        html_text = fetch_page_with_retries(page)

        if html_text is None:
            page += 1
            time.sleep(DELAY_SECONDS)
            continue

        results = extract_results_from_html(html_text)

        if last_page is None:
            last_page = results["meta"]["last_page"]
            print(f"Last available page: {last_page}")

        page_records = results["data"]

        if not page_records:
            print("No records found. Stopping.")
            break

        cleaned_records = [clean_record(record) for record in page_records]
        all_records.extend(cleaned_records)
        all_records = _deduplicate_by_url(all_records)

        if len(all_records) > target_records:
            all_records = all_records[:target_records]

        save_data(all_records)

        print(f"Collected {len(all_records)} records.")

        if page >= last_page:
            print("Reached final page. Stopping.")
            break

        page += 1
        time.sleep(DELAY_SECONDS)

    return all_records


if __name__ == "__main__":  # pragma: no cover
    records = scrape_data()
    save_data(records)
    print(f"Saved {len(records)} records to {OUTPUT_FILE}")
