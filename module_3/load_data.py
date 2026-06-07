import json
import psycopg
from datetime import datetime

DB_NAME = "gradcafe_db"
DB_USER = "postgres"
DB_PASSWORD = "HKZ012514"
DB_HOST = "localhost"
DB_PORT = "5432"

DATA_FILE = "cleaned_applicant_data.json"


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


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

    cur = conn.cursor()

    cur.execute("DELETE FROM applicants;")

    insert_sql = """
        INSERT INTO applicants (
            p_id, program, comments, date_added, url, status, term,
            us_or_international, gpa, gre, gre_v, gre_aw, degree,
            llm_generated_program, llm_generated_university
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for item in data:
        cur.execute(insert_sql, (
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
        ))

    conn.commit()
    cur.close()
    conn.close()

    print(f"Loaded {len(data)} records into applicants table.")


if __name__ == "__main__":
    main()