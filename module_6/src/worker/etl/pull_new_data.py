"""
Pull additional GradCafe applicant records and update PostgreSQL.

This module scrapes new GradCafe pages, cleans the records,
saves intermediate JSON files, and inserts new records into
the applicants database while avoiding duplicates.
"""
import os
import json
import time

import psycopg

from dotenv import load_dotenv

from src.db.load_data import get_watermark, update_watermark
from src.worker.etl.scrape import (
    fetch_page_with_retries,
    extract_results_from_html,
    clean_record,
)
from src.worker.etl.clean import clean_data

load_dotenv()

TARGET_RECORDS = 500
RECORDS_PER_PAGE = 20

RAW_OUTPUT_FILE = "additional_applicant_data.json"
CLEAN_OUTPUT_FILE = "additional_cleaned_applicant_data.json"

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}


def to_float(value):
    """Convert a value to float, returning None for invalid inputs."""
    if value in (None, "", "None"):
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def to_int(value):
    """Convert a value to integer, returning None for invalid inputs."""
    if value in (None, "", "None"):
        return None

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def save_json(data, filename):
    """save the data as the josn file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_start_page():
    """Return starting GradCafe page based on ingestion watermark."""
    last_seen = get_watermark()
    start_page = last_seen // RECORDS_PER_PAGE + 50

    print(f"Current watermark: {last_seen}", flush=True)
    print(f"Calculated start page: {start_page}", flush=True)

    return start_page


def scrape_new_records():
    """
    Scrape approximately 500 new GradCafe records.

    Returns:
        list:
            List of cleaned applicant records.
    """
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
    """
    Insert new applicant records into PostgreSQL.

    Args:
        records (list):
            Cleaned applicant records.

    Returns:
        tuple:
            (inserted_count, skipped_count)
    """
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
    """
    Execute the complete data pull workflow.

    The workflow:
    1. Scrapes new records.
    2. Saves raw JSON.
    3. Cleans records.
    4. Saves cleaned JSON.
    5. Inserts records into PostgreSQL.
    """
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

    current_watermark = get_watermark()
    update_watermark(current_watermark + inserted)

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
