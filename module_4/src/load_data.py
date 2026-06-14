import json
import os
import psycopg
from datetime import datetime

DATA_FILE = "cleaned_applicant_data.json"

DEFAULT_DATABASE_URL = "postgresql://postgres:HKZ012514@localhost:5432/gradcafe_db"


def get_database_url():
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_connection():
    return psycopg.connect(get_database_url())


def create_table():
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


def parse_float(value):
    if value in (None, "", "None", "null"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%b %d, %Y").date()
    except ValueError:
        return None


def record_to_tuple(item):
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
    create_table()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM applicants;")
            return cur.fetchone()[0]


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    inserted = load_records(data)
    print(f"Inserted {inserted} new records into applicants table.")


if __name__ == "__main__": # pragma: no cover
    main()