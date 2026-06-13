# GradCafe Analytics Dashboard (Module 3)

## Project Overview

This project analyzes graduate school admissions data from GradCafe using PostgreSQL and Flask. The workflow includes:

1. Scraping and cleaning GradCafe application records
2. Loading records into PostgreSQL
3. Running SQL analytics queries
4. Displaying results in a Flask dashboard
5. Pulling additional records and updating the database

---

## Repository Structure

```text
module_3/
├── app.py
├── load_data.py
├── query_data.py
├── pull_new_data.py
├── requirements.txt
├── README.md
├── limitations.pdf
├── cleaned_applicant_data.json
├── additional_applicant_data.json
├── additional_cleaned_applicant_data.json
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── screenshots/
│   ├── console_query_output.png
│   ├── flask_dashboard.png
│   ├── pulling_data.png
│   └── data_pulled_and_analysis_updated.png
└── module_2_code/
```

---

## Environment Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## PostgreSQL Setup

Create the database:

```sql
CREATE DATABASE gradcafe_db;
```

Connect to the database:

```sql
\c gradcafe_db
```

---

## Load Initial Data

Load the cleaned GradCafe records into PostgreSQL:

```bash
python load_data.py
```

This creates and populates the applicants table.

---

## Run Analytics Queries

Execute:

```bash
python query_data.py
```

This runs all SQL queries and prints answers for Questions 1–11 in the terminal.

Example output:

```text
Q1
33051 Fall 2026 entries

Q2
47.66% International students

...
```

---

## Launch the Flask Dashboard

Start the web application:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

The dashboard displays:

* Current database size
* Pull Data status
* SQL analytics results

---

## Pull New Data

Click:

```text
Pull Data
```

The application:

1. Determines the current database size
2. Calculates a starting GradCafe page dynamically
3. Scrapes approximately 500 additional records
4. Cleans the records
5. Inserts non-duplicate records into PostgreSQL

The dashboard status panel updates automatically to indicate:

```text
Pull Data is currently running
```

and later:

```text
No data pull is currently running.
New data has been added if available.
Click Update Analysis to refresh the SQL results.
```

---

## Refresh Analytics

Click:

```text
Update Analysis
```

This reruns all SQL queries against the latest PostgreSQL database contents and refreshes the dashboard results.

---

## Screenshots

The screenshots directory contains:

* console_query_output.png
* flask_dashboard.png
* pulling_data.png
* data_pulled_and_analysis_updated.png

These demonstrate the SQL query output, Flask dashboard, live data pull workflow, and refreshed analytics.

---

## Limitations

See:

```text
limitations.pdf
```

for a discussion of the limitations of analyzing anonymously submitted admissions data and potential sources of bias.

---

## Author

Hongkang Zhang

Johns Hopkins University

Software Concepts – Module 3
