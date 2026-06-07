# Module 3 - PostgreSQL Analysis of GradCafe Data

## Overview

This project loads cleaned GradCafe applicant data into PostgreSQL and performs SQL-based analysis using Python.

The project includes:

* `load_data.py` – loads applicant records into PostgreSQL
* `query_data.py` – answers Questions 1–8 using SQL queries
* `q9_llm.py` – answers Question 9 using LLM-generated program and university fields
* `cleaned_applicant_data.json` – cleaned applicant dataset (~35,000 records)
* `llm_extend_applicant_data_full.jsonl` – LLM-processed dataset containing normalized program and university fields

---

## Requirements

### Python Packages

Install psycopg:

```bash
pip install "psycopg[binary]"
```

### PostgreSQL

Create a PostgreSQL database named:

```sql
CREATE DATABASE gradcafe_db;
```

---

## Project Structure

```text
module_3/
│
├── cleaned_applicant_data.json
├── llm_extend_applicant_data_full.jsonl
├── load_data.py
├── query_data.py
├── q9_llm.py
└── README.md
```

---

## Loading the Data

Load the cleaned applicant dataset into PostgreSQL:

```bash
python load_data.py
```

Expected output:

```text
Loaded 35000 records into applicants table.
```

---

## Running Questions 1–8

Execute:

```bash
python query_data.py
```

This script connects to PostgreSQL and executes SQL queries to answer Questions 1–8.

### Results

| Question | Result                                                                                                 |
| -------- | ------------------------------------------------------------------------------------------------------ |
| Q1       | 33,051 Fall 2026 entries                                                                               |
| Q2       | 44.85% International students                                                                          |
| Q3       | GPA = 3.77, GRE = 325.08, GRE-V = 160.64, GRE-AW = 4.35                                                |
| Q4       | Average GPA of American Fall 2026 applicants = 3.79                                                    |
| Q5       | Acceptance rate for Fall 2026 = 35.84%                                                                 |
| Q6       | Average GPA of accepted Fall 2026 applicants = 3.77                                                    |
| Q7       | JHU Computer Science Master's applicants = 9                                                           |
| Q8       | Accepted 2026 PhD Computer Science applicants from Georgetown, MIT, Stanford, and Carnegie Mellon = 15 |

---

## Running Question 9

Question 9 uses the LLM-generated fields to compare results obtained from normalized data versus the original downloaded fields.

Execute:

```bash
python q9_llm.py
```

The script analyzes:

* `llm-generated-program`
* `llm-generated-university`

### Result

Using the original downloaded fields, Question 8 identified **15** accepted PhD applicants in Computer Science from Georgetown University, MIT, Stanford University, and Carnegie Mellon University for 2026.

Using the LLM-generated program and university fields, Question 9 also returned **15** matching applicants.

Therefore, the LLM-generated fields produced the same final result as the original downloaded fields for this analysis.

---

## Notes

The LLM-processed dataset preserves the original scraped information while adding normalized fields:

```text
llm-generated-program
llm-generated-university
```

These fields allow structured analysis across records with varying naming conventions.

---

## Author

Hongkang Zhang

Johns Hopkins University

Software Concepts – Module 3
