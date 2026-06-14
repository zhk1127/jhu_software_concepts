# GradCafe Analytics Dashboard (Module 4)

## Project Overview

This project analyzes graduate school admissions data from GradCafe using PostgreSQL and Flask. The workflow includes:

1. Scraping and cleaning GradCafe application records
2. Loading records into PostgreSQL
3. Running SQL analytics queries
4. Displaying results in a Flask dashboard
5. Pulling additional records and updating the database
6. Automated testing with pytest
7. Continuous integration using GitHub Actions
8. Sphinx documentation generation

---

## Repository Structure

```text
module_4/
├── src/
│   ├── app.py
│   ├── load_data.py
│   ├── query_data.py
│   └── pull_new_data.py
├── tests/
├── docs/
├── .github/
│   └── workflows/
│       └── tests.yml
├── requirements.txt
├── README.md
├── limitations.pdf
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── screenshots/
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

Update database credentials in the source files if necessary.

---

## Load Initial Data

Load the cleaned GradCafe records into PostgreSQL:

```bash
python -m src.load_data
```

This creates and populates the `applicants` table.

---

## Run Analytics Queries

Execute:

```bash
python -m src.query_data
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
python -m src.app
```

Open:

```text
http://127.0.0.1:5000/analysis
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

## Automated Testing

The project includes a comprehensive pytest suite covering:

* Flask routes
* Database operations
* Data loading workflows
* Pull Data functionality
* Analysis updates
* Utility functions

Run all tests:

```bash
python -m pytest tests
```

Current test results:

```text
28 passed
```

---

## Test Coverage

Coverage is measured using pytest-cov.

Run:

```bash
python -m pytest tests --cov=src --cov-report=term-missing
```

Current coverage:

```text
100% coverage
```

for all source files under `src/`.

Command-line entry-point sections are excluded using the standard `coverage.py` mechanism (`# pragma: no cover`) so that coverage reflects application logic rather than script-launch boilerplate.

---

## Continuous Integration

GitHub Actions automatically validates every push to the repository.

The workflow:

1. Starts a PostgreSQL service
2. Creates the GradCafe database
3. Installs project dependencies
4. Loads test data
5. Runs the full pytest suite
6. Verifies coverage requirements

Workflow configuration:

```text
.github/workflows/tests.yml
```

---

## Documentation

Sphinx documentation is provided in:

```text
docs/
```

Generate documentation:

```bash
cd docs

python -m sphinx -b html source build/html
```

Open:

```text
docs/build/html/index.html
```

Documentation includes:

* Architecture overview
* ETL workflow
* Database layer
* Analysis layer
* Flask web layer
* Automatically generated API reference pages

---

## Screenshots

The screenshots directory contains examples of:

* SQL query output
* Flask dashboard
* Pull Data workflow
* Updated analytics
* GitHub Actions execution
* Coverage results

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

Software Concepts – Module 4
