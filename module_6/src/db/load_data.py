"""
Load cleaned GradCafe applicant records into PostgreSQL.

This module creates the applicants table, loads applicant
records from JSON files, and provides helper functions for
database access, record conversion, and ingestion watermarks.
"""
import json
import os

from datetime import datetime

import psycopg
from dotenv import load_dotenv

load_dotenv()
DATA_FILE = "src/data/cleaned_applicant_data.json"


def get_database_url():
    """Return the PostgreSQL connection URL."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "gradcafe_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")

    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def get_connection():
    """Create and return a PostgreSQL database connection."""
    return psycopg.connect(get_database_url())


def create_table():
    """Create required database tables if they do not already exist."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS applicants (
                    p_id TEXT PRIMARY KEY,
                    program TEXT,
                    comments TEXT,
                    date_added DATE,
                    url TEXT,
                    status TEXT,
                    term TEXT,
                    us_or_international TEXT,
                    gpa DOUBLE PRECISION,
                    gre DOUBLE PRECISION,
                    gre_v DOUBLE PRECISION,
                    gre_aw DOUBLE PRECISION,
                    degree TEXT,
                    llm_generated_program TEXT,
                    llm_generated_university TEXT
                );
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS ingestion_watermarks (
                    source TEXT PRIMARY KEY,
                    last_seen INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )


def parse_float(value):
    """Convert a value to float, returning None for invalid inputs."""
    if value in (None, "", "None", "null"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_date(value):
    """Convert a date string into a Python date object."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%b %d, %Y").date()
    except ValueError:
        return None


def record_to_tuple(item):
    """Convert an applicant record dictionary into a database-ready tuple."""
    return (
        item.get("raw_record", {}).get("id"),
        item.get("program"),
        item.get("comments"),
        parse_date(item.get("date_added")),
        item.get("url"),
        item.get("status"),
        item.get("term"),
        item.get("US/International"),
        parse_float(item.get("GPA")),
        parse_float(item.get("GRE Score")),
        parse_float(item.get("GRE V Score")),
        parse_float(item.get("GRE AW")),
        item.get("Degree"),
        item.get("llm-generated-program"),
        item.get("llm-generated-university"),
    )


def load_records(data):
    """Insert applicant records into PostgreSQL with idempotent conflict handling."""
    create_table()

    insert_sql = """
        INSERT INTO applicants (
            p_id, program, comments, date_added, url, status, term,
            us_or_international, gpa, gre, gre_v, gre_aw, degree,
            llm_generated_program, llm_generated_university
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (p_id) DO NOTHING
    """

    inserted = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            for item in data:
                cur.execute(insert_sql, record_to_tuple(item))
                inserted += cur.rowcount

    return inserted


def get_database_count():
    """Return the total number of records in the applicants table."""
    create_table()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM applicants;")
            return cur.fetchone()[0]


def get_watermark(source="gradcafe"):
    """Return the current ingestion watermark for a source."""
    create_table()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT last_seen
                FROM ingestion_watermarks
                WHERE source = %s;
                """,
                (source,),
            )
            row = cur.fetchone()

    return row[0] if row else 0


def update_watermark(last_seen, source="gradcafe"):
    """Insert or update the ingestion watermark for a source."""
    create_table()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ingestion_watermarks (source, last_seen)
                VALUES (%s, %s)
                ON CONFLICT (source)
                DO UPDATE SET
                    last_seen = EXCLUDED.last_seen,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (source, last_seen),
            )


def main():
    """Load the initial cleaned applicant dataset."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    inserted = load_records(data)
    current_count = get_database_count()
    update_watermark(current_count)

    print(f"Inserted {inserted} new records into applicants table.")
    print(f"Updated ingestion watermark to {current_count}.")


if __name__ == "__main__":  # pragma: no cover
    main()
