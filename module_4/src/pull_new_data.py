import json
import time
import sys

import psycopg

sys.path.append("module_2_code")

from scrape import fetch_page_with_retries, extract_results_from_html, clean_record
from clean import clean_data

TARGET_RECORDS = 500
RECORDS_PER_PAGE = 20

RAW_OUTPUT_FILE = "additional_applicant_data.json"
CLEAN_OUTPUT_FILE = "additional_cleaned_applicant_data.json"

DB_CONFIG = {
    "dbname": "gradcafe_db",
    "user": "postgres",
    "password": "HKZ012514",
    "host": "localhost",
    "port": "5432",
}


def to_float(value):
    if value in (None, "", "None"):
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def to_int(value):
    if value in (None, "", "None"):
        return None

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_start_page():
    conn = psycopg.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM applicants;")
    record_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    start_page = record_count // RECORDS_PER_PAGE + 50

    print(f"Current database records: {record_count}", flush=True)
    print(f"Calculated start page: {start_page}", flush=True)

    return start_page


def scrape_new_records():
    all_records = []

    page = get_start_page()

    print(f"Starting scrape from page {page}", flush=True)
    print(f"Target records: {TARGET_RECORDS}", flush=True)

    while len(all_records) < TARGET_RECORDS:
        print(f"Fetching page {page}...", flush=True)

        html_text = fetch_page_with_retries(page)

        if html_text is None:
            page += 1
            continue

        results = extract_results_from_html(html_text)
        page_records = results["data"]

        if not page_records:
            print("No records found. Stopping.", flush=True)
            break

        cleaned_page_records = [
            clean_record(record)
            for record in page_records
        ]

        all_records.extend(cleaned_page_records)

        print(f"Collected {len(all_records)} records", flush=True)

        page += 1
        time.sleep(1)

    return all_records[:TARGET_RECORDS]


def insert_records_into_database(records):
    conn = psycopg.connect(**DB_CONFIG)
    cur = conn.cursor()

    inserted = 0
    skipped = 0

    for record in records:
        raw_record = record.get("raw_record") or {}
        p_id = raw_record.get("id")

        if p_id is None:
            skipped += 1
            continue

        cur.execute(
            """
            INSERT INTO applicants (
                p_id,
                program,
                comments,
                url,
                status,
                term,
                us_or_international,
                degree,
                gpa,
                gre,
                gre_v,
                gre_aw,
                date_added,
                llm_generated_program,
                llm_generated_university
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            ON CONFLICT (p_id) DO NOTHING;
            """,
            (
                p_id,
                record.get("program"),
                record.get("comments"),
                record.get("url"),
                record.get("status"),
                record.get("term"),
                record.get("US/International"),
                record.get("Degree"),
                to_float(record.get("GPA")),
                to_int(record.get("GRE Score")),
                to_int(record.get("GRE V Score")),
                to_float(record.get("GRE AW")),
                record.get("date_added"),
                None,
                None,
            ),
        )

        if cur.rowcount == 1:
            inserted += 1
        else:
            skipped += 1

    conn.commit()
    cur.close()
    conn.close()

    return inserted, skipped


def main():
    raw_records = scrape_new_records()

    save_json(raw_records, RAW_OUTPUT_FILE)
    print(
        f"Saved {len(raw_records)} records to {RAW_OUTPUT_FILE}",
        flush=True
    )

    cleaned_records = clean_data(raw_records)

    save_json(cleaned_records, CLEAN_OUTPUT_FILE)
    print(
        f"Saved {len(cleaned_records)} records to {CLEAN_OUTPUT_FILE}",
        flush=True
    )

    inserted, skipped = insert_records_into_database(cleaned_records)

    print(
        f"Inserted {inserted} new records into PostgreSQL.",
        flush=True
    )

    print(
        f"Skipped {skipped} duplicate or invalid records.",
        flush=True
    )

    print("Pull Data completed successfully.", flush=True)


if __name__ == "__main__": # pragma: no cover
    main()