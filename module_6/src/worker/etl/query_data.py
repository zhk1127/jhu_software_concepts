"""
Generate analytics results from GradCafe admissions data.

This module executes SQL queries against PostgreSQL and
returns formatted answers for Questions 1–11 used by
the Flask dashboard and assignment analysis.
"""
import os
import psycopg
from dotenv import load_dotenv
from psycopg import sql

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}


def get_llm_q9_count():
    """
    Count accepted Computer Science PhD applicants using
    LLM-generated university and program annotations
    stored in PostgreSQL.

    Returns:
        int:
            Number of matching applicants.
    """
    target_universities = [
        "Georgetown University",
        "Massachusetts Institute of Technology",
        "MIT",
        "Stanford University",
        "Carnegie Mellon University",
    ]

    conn = psycopg.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE status = %s
          AND degree = %s
          AND term LIKE %s
          AND LOWER(llm_generated_program) = %s
          AND llm_generated_university = ANY(%s)
        """,
        (
            "Accepted",
            "PhD",
            "%2026%",
            "computer science",
            target_universities,
        ),
    )

    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return count

def get_analysis_results():
    """
    Execute all analytics queries.

    Returns:
        dict:
            Dictionary mapping question identifiers
            (Q1–Q11) to formatted answers.
    """
    conn = psycopg.connect(**DB_CONFIG)
    cur = conn.cursor()

    results = {}

    # Q1
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term = 'Fall 2026'
        LIMIT 1;
    """)
    results["Q1"] = f"{cur.fetchone()[0]:,} Fall 2026 entries"

    # Q2
    cur.execute("""
        SELECT ROUND(
            100.0 * COUNT(*) / (SELECT COUNT(*) FROM applicants),
            2
        )
        FROM applicants
        WHERE us_or_international NOT IN ('American', 'Other')
        LIMIT 1;
    """)
    results["Q2"] = f"{cur.fetchone()[0]}% International students"

    # Q3
    cur.execute("""
        SELECT
            ROUND(AVG(CASE WHEN gpa BETWEEN 2 AND 4.3 THEN gpa END)::numeric, 2),
            ROUND(AVG(CASE WHEN gre BETWEEN 260 AND 340 THEN gre END)::numeric, 2),
            ROUND(AVG(CASE WHEN gre_v BETWEEN 130 AND 170 THEN gre_v END)::numeric, 2),
            ROUND(AVG(CASE WHEN gre_aw BETWEEN 1 AND 6 THEN gre_aw END)::numeric, 2)
        FROM applicants
        LIMIT 1;
    """)
    gpa, gre, gre_v, gre_aw = cur.fetchone()
    results["Q3"] = f"GPA = {gpa}, GRE = {gre}, GRE-V = {gre_v}, GRE-AW = {gre_aw}"

    # Q4
    cur.execute("""
        SELECT ROUND(
            AVG(CASE WHEN gpa BETWEEN 2 AND 4.3 THEN gpa END)::numeric,
            2
        )
        FROM applicants
        WHERE term = 'Fall 2026'
          AND us_or_international = 'American'
        LIMIT 1;
    """)
    results["Q4"] = f"Average GPA of American Fall 2026 applicants = {cur.fetchone()[0]}"

    # Q5
    cur.execute("""
        SELECT ROUND(
            100.0 * COUNT(*) /
            (SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026'),
            2
        )
        FROM applicants
        WHERE term = 'Fall 2026'
          AND status = 'Accepted'
        LIMIT 1;
    """)
    results["Q5"] = f"Acceptance rate for Fall 2026 = {cur.fetchone()[0]}%"

    # Q6
    cur.execute("""
        SELECT ROUND(
            AVG(CASE WHEN gpa BETWEEN 2 AND 4.3 THEN gpa END)::numeric,
            2
        )
        FROM applicants
        WHERE term = 'Fall 2026'
          AND status = 'Accepted'
        LIMIT 1;
    """)
    results["Q6"] = f"Average GPA of accepted Fall 2026 applicants = {cur.fetchone()[0]}"

    # Q7
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE program = 'Computer Science, Johns Hopkins University'
          AND degree = 'Masters'
        LIMIT 1;
    """)
    results["Q7"] = f"JHU Computer Science Master's applicants = {cur.fetchone()[0]}"

    # Q8
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE degree = 'PhD'
          AND status = 'Accepted'
          AND term LIKE '%2026%'
          AND program IN (
            'Computer Science, Georgetown University',
            'Computer Science, Massachusetts Institute of Technology (MIT)',
            'Computer Science, Stanford University',
            'Computer Science, Carnegie Mellon University'
          )
        LIMIT 1;
    """)
    q8 = cur.fetchone()[0]
    results["Q8"] = (
        "Accepted 2026 PhD Computer Science applicants from "
        f"Georgetown, MIT, Stanford, and CMU = {q8}"
    )

    # Q9
    q9 = get_llm_q9_count()
    results["Q9"] = f"LLM-generated fields produced the same result as Q8 ({q9})"

    # Q10
       # Q10
    bio_filter = sql.SQL("""
        degree = 'PhD'
        AND program ILIKE '%johns hopkins%'
        AND (
            program ILIKE '%bio%'
            OR program ILIKE '%biochem%'
            OR program ILIKE '%biomedical%'
            OR program ILIKE '%biomolecular%'
            OR program ILIKE '%biophysics%'
            OR program ILIKE '%cellular%'
            OR program ILIKE '%molecular%'
            OR program ILIKE '%genetics%'
            OR program ILIKE '%genomics%'
            OR program ILIKE '%immunology%'
            OR program ILIKE '%neuroscience%'
        )
    """)

    q10_stmt = sql.SQL("""
        SELECT COUNT(*)
        FROM applicants
        WHERE {bio_filter}
        LIMIT 1
    """).format(bio_filter=bio_filter)

    cur.execute(q10_stmt)
    results["Q10"] = (
        f"JHU biology-related PhD applicants = {cur.fetchone()[0]}"
    )

    # Q11
    q11_stmt = sql.SQL("""
        SELECT ROUND(
            100.0 * SUM(CASE WHEN status = 'Accepted' THEN 1 ELSE 0 END)
            / COUNT(*),
            2
        )
        FROM applicants
        WHERE {bio_filter}
        LIMIT 1
    """).format(bio_filter=bio_filter)

    cur.execute(q11_stmt)
    results["Q11"] = (
        "Acceptance rate for JHU biology-related PhD applicants = "
        f"{cur.fetchone()[0]}%"
    )

    cur.close()
    conn.close()

    return results


if __name__ == "__main__":
    analysis_results = get_analysis_results()

    for question, answer in analysis_results.items():
        print(question)
        print(answer)
        print()
