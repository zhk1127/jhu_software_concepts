# Module 3 - PostgreSQL and Flask Analysis

## Overview

This project loads GradCafe application data into a PostgreSQL database, performs SQL analysis, and displays the results through a Flask web application.

The dataset contains approximately 35,000 GradCafe application records.

---

## Files

### Core Files

* `load_data.py` – Loads JSON application records into PostgreSQL
* `query_data.py` – Executes SQL queries (Q1–Q11)
* `q9_llm.py` – Evaluates Question 9 using LLM-generated fields
* `app.py` – Flask web application
* `requirements.txt` – Python package requirements

### Data Files

* `cleaned_applicant_data.json` – Source dataset (~35,000 records)
* `llm_extend_applicant_data_full.jsonl` – LLM-processed dataset with standardized program and university fields

### Flask Files

* `templates/index.html` – Main analysis webpage
* `static/style.css` – Page styling

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

**Answer:** 9

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

The webpage displays the results of Questions Q1–Q11 in a formatted table.

---

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Required packages:

* Flask
* psycopg2-binary
