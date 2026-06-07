# Module 3 - PostgreSQL and Flask Analysis

## Overview

This project loads GradCafe application data into a PostgreSQL database, performs SQL analysis, and displays the results through a Flask web application.

The original dataset contains approximately 35,000 GradCafe application records. During Part B testing, additional records were successfully scraped and inserted, increasing the database size to approximately 36,000 records.

---

## Files

### Core Files

* `load_data.py` – Loads JSON application records into PostgreSQL
* `query_data.py` – Executes SQL queries (Q1–Q11)
* `q9_llm.py` – Evaluates Question 9 using LLM-generated fields
* `pull_new_data.py` – Reuses Module 2 scraping and cleaning code to retrieve additional GradCafe records and insert them into PostgreSQL
* `app.py` – Flask web application
* `requirements.txt` – Python package requirements

### Data Files

* `cleaned_applicant_data.json` – Original dataset (~35,000 records)
* `additional_cleaned_applicant_data.json` – Additional records scraped during Pull Data operations
* `llm_extend_applicant_data_full.jsonl` – LLM-processed dataset with standardized program and university fields

### Flask Files

* `templates/index.html` – Main analysis webpage
* `static/style.css` – Page styling

### Reused Module 2 Files

* `module_2_code/scrape.py`
* `module_2_code/clean.py`

These files are reused by the Pull Data workflow.

---

## Database Setup

Create database:

```sql
CREATE DATABASE gradcafe_db;
```

Load data:

```bash
python load_data.py
```

Expected output:

```text
Loaded 35000 records into applicants table.
```

---

## SQL Analysis Results

### Q1

How many entries applied for Fall 2026?

**Answer:** 33,051

### Q2

What percentage of entries are international students?

**Answer:** 44.85%

### Q3

Average GPA, GRE, GRE-V, and GRE-AW?

**Answer:**

* GPA = 3.77
* GRE = 325.08
* GRE-V = 160.64
* GRE-AW = 4.35

### Q4

Average GPA of American applicants for Fall 2026?

**Answer:** 3.79

### Q5

Acceptance rate for Fall 2026?

**Answer:** 35.84%

### Q6

Average GPA of accepted Fall 2026 applicants?

**Answer:** 3.77

### Q7

Number of Johns Hopkins Computer Science Master's applicants?

**Answer:** 15

### Q8

Accepted 2026 PhD Computer Science applicants from Georgetown, MIT, Stanford, and Carnegie Mellon?

**Answer:** 15

### Q9

Do results change when using LLM-generated fields?

**Answer:** No.

The LLM-generated dataset produced the same result as Q8.

* Original dataset result: 15
* LLM dataset result: 15

### Q10

How many applicants applied to Johns Hopkins University PhD programs in biology-related fields?

**Answer:** 39

### Q11

What is the acceptance rate of applicants who applied to Johns Hopkins University PhD programs in biology-related fields?

**Answer:** 20.51%

---

## Part B - Pull Data Feature

A new **Pull Data** button was added to the Flask dashboard.

When clicked:

1. Module 2 scraping code is executed.
2. Approximately 500 additional GradCafe records are scraped.
3. Records are cleaned using the Module 2 cleaning pipeline.
4. Records are inserted into PostgreSQL.
5. Duplicate records are skipped using the applicant identifier (`p_id`).
6. The webpage automatically displays pull status information.
7. Multiple concurrent pull requests are prevented.

Example output:

```text
Collected 500 records
Saved 500 records to additional_cleaned_applicant_data.json
Inserted 1 new record into PostgreSQL
Skipped 499 duplicate or invalid records
Pull Data completed successfully
```

---

## Part B - Update Analysis Feature

A new **Update Analysis** button was added to the Flask dashboard.

The button:

* Refreshes all SQL query results
* Uses the latest contents of PostgreSQL
* Is disabled while a Pull Data operation is running

The dashboard also displays:

* Current database size
* Current pull status
* Whether the application is ready for analysis

---

## Running the SQL Analysis

```bash
python query_data.py
```

---

## Running the Flask Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

The webpage displays the results of Questions Q1–Q11 and provides Pull Data and Update Analysis functionality.

---

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Required packages:

* Flask
* psycopg
* BeautifulSoup4
* Requests

---

## Limitations

* GradCafe data quality depends on user-submitted information.
* Some records contain missing GPA or GRE values.
* Pull Data currently scrapes a fixed number of records per run.
* Most SQL analysis uses original database fields.
* Only Question 9 depends on LLM-generated standardized fields.
* Flask is run using the built-in development server and is not intended for production deployment.
