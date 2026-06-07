# Module 3 - PostgreSQL Analysis

## Overview

This module loads GradCafe applicant data into PostgreSQL and performs SQL-based analysis.

## Setup

Install PostgreSQL and psycopg:

```bash
pip install "psycopg[binary]"
```

Create database:

```sql
CREATE DATABASE gradcafe_db;
```

## Load Data

Run:

```bash
python load_data.py
```

This loads approximately 35,000 applicant records into the `applicants` table.

## Run Analysis

Run:

```bash
python query_data.py
```

Current results:

| Question | Result                                          |
| -------- | ----------------------------------------------- |
| Q1       | 33,051                                          |
| Q2       | 44.85%                                          |
| Q3       | GPA 3.77, GRE 325.08, GRE-V 160.64, GRE-AW 4.35 |
| Q4       | 3.79                                            |
| Q5       | 35.84%                                          |
| Q6       | 3.77                                            |
| Q7       | 9                                               |
| Q8       | 15                                              |

## Remaining Work

* Q9 (LLM-generated fields comparison)
* Flask web interface
* Final writeup
