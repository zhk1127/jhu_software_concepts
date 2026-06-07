import psycopg

conn = psycopg.connect(
    dbname="gradcafe_db",
    user="postgres",
    password="HKZ012514",
    host="localhost",
    port="5432"
)

print("Connected to gradcafe_db")

cur = conn.cursor()

# Question 1
cur.execute("""
SELECT COUNT(*)
FROM applicants
WHERE term = 'Fall 2026';
""")

result = cur.fetchone()[0]

print("\nQuestion 1")
print("How many entries applied for Fall 2026?")
print(result)


# Question 2
cur.execute("""
SELECT ROUND(
    100.0 * COUNT(*) /
    (SELECT COUNT(*) FROM applicants),
    2
)
FROM applicants
WHERE us_or_international = 'International';
""")

result = cur.fetchone()[0]

print("\nQuestion 2")
print("What percentage of entries are from international students?")
print(result, "%")

# Question 3
# Note:
# GradCafe provides GRE General (total), GRE Verbal, and GRE AW.
# Invalid placeholder values (e.g. 0, 99.99) are excluded.

cur.execute("""
SELECT
    ROUND(
        AVG(
            CASE
                WHEN gpa BETWEEN 2 AND 4.3 THEN gpa
                ELSE NULL
            END
        )::numeric, 2
    ),

    ROUND(
        AVG(
            CASE
                WHEN gre BETWEEN 260 AND 340 THEN gre
                ELSE NULL
            END
        )::numeric, 2
    ),

    ROUND(
        AVG(
            CASE
                WHEN gre_v BETWEEN 130 AND 170 THEN gre_v
                ELSE NULL
            END
        )::numeric, 2
    ),

    ROUND(
        AVG(
            CASE
                WHEN gre_aw BETWEEN 1 AND 6 THEN gre_aw
                ELSE NULL
            END
        )::numeric, 2
    )

FROM applicants;
""")

gpa_avg, gre_avg, gre_v_avg, gre_aw_avg = cur.fetchone()

print("\nQuestion 3")
print("What is the average GPA, GRE, GRE V, and GRE AW of applicants who provide these metrics?")
print("Average GPA:", gpa_avg)
print("Average GRE General:", gre_avg)
print("Average GRE Verbal:", gre_v_avg)
print("Average GRE AW:", gre_aw_avg)

# Question 4
cur.execute("""
SELECT
    ROUND(
        AVG(
            CASE
                WHEN gpa BETWEEN 2 AND 4.3 THEN gpa
                ELSE NULL
            END
        )::numeric,
        2
    )
FROM applicants
WHERE term = 'Fall 2026'
  AND us_or_international = 'American';
""")

avg_gpa_american_fall_2026 = cur.fetchone()[0]

print("\nQuestion 4")
print("What is the average GPA of American students in Fall 2026?")
print("Average GPA:", avg_gpa_american_fall_2026)


# Question 5

cur.execute("""
SELECT
    ROUND(
        100.0 * COUNT(*) /
        (
            SELECT COUNT(*)
            FROM applicants
            WHERE term = 'Fall 2026'
        ),
        2
    )
FROM applicants
WHERE term = 'Fall 2026'
  AND status = 'Accepted';
""")

acceptance_rate = cur.fetchone()[0]

print("\nQuestion 5")
print("What percent of Fall 2026 entries are Acceptances?")
print(f"{acceptance_rate} %")

# Question 6

cur.execute("""
SELECT
    ROUND(
        AVG(
            CASE
                WHEN gpa BETWEEN 2 AND 4.3 THEN gpa
                ELSE NULL
            END
        )::numeric,
        2
    )
FROM applicants
WHERE term = 'Fall 2026'
  AND status = 'Accepted';
""")

avg_gpa_accepted = cur.fetchone()[0]

print("\nQuestion 6")
print("What is the average GPA of accepted applicants for Fall 2026?")
print("Average GPA:", avg_gpa_accepted)

# Question 7

cur.execute("""
SELECT COUNT(*)
FROM applicants
WHERE program = 'Computer Science, Johns Hopkins University'
  AND degree = 'Masters';
""")

jhu_cs_masters = cur.fetchone()[0]

print("\nQuestion 7")
print("How many entries are from applicants who applied to JHU for a masters degree in Computer Science?")
print(jhu_cs_masters)


# Question 8

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
  );
""")

q8_result = cur.fetchone()[0]

print("\nQuestion 8")
print("How many 2026 acceptances are from applicants who applied to Georgetown, MIT, Stanford, or CMU for a PhD in Computer Science?")
print(q8_result)

# Question 10
cur.execute("""
SELECT COUNT(*)
FROM applicants
WHERE degree = 'PhD'
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
  );
""")

jhu_bio_phd_count = cur.fetchone()[0]

print("\nQuestion 10")
print("How many applicants applied to Johns Hopkins University PhD programs in biology-related fields?")
print(jhu_bio_phd_count)


# Question 11
cur.execute("""
SELECT ROUND(
    100.0 * SUM(
        CASE
            WHEN status = 'Accepted' THEN 1
            ELSE 0
        END
    ) / COUNT(*),
    2
)
FROM applicants
WHERE degree = 'PhD'
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
  );
""")

jhu_bio_phd_acceptance_rate = cur.fetchone()[0]

print("\nQuestion 11")
print("What is the acceptance rate of applicants who applied to Johns Hopkins University PhD programs in biology-related fields?")
print(f"{jhu_bio_phd_acceptance_rate} %")


cur.close()
conn.close()

print("\nDatabase connection closed.")