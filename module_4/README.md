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
9. Read the Docs deployment

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
├── coverage_summary.txt
├── actions_success.png
├── limitations.pdf
├── templates/
├── static/
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

```bash
python -m src.load_data
```

This creates and populates the applicants table.

---

## Run Analytics Queries

```bash
python -m src.query_data
```

This executes all SQL analysis queries and prints answers for Questions 1–11.

---

## Launch the Flask Dashboard

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

The **Pull Data** button:

1. Determines current database size
2. Calculates the appropriate starting GradCafe page
3. Scrapes approximately 500 new records
4. Cleans and standardizes records
5. Inserts non-duplicate records into PostgreSQL

---

## Refresh Analytics

The **Update Analysis** button reruns all SQL queries and refreshes dashboard results using the latest database contents.

---

## Automated Testing

The project includes comprehensive pytest coverage for:

* Flask routes
* Database operations
* Data loading workflows
* Pull Data functionality
* Analysis updates
* Integration workflows

Run all tests:

```bash
python -m pytest tests
```

Current result:

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

Current result:

```text
100% coverage
```

Coverage proof is included in:

```text
coverage_summary.txt
```

---

## Continuous Integration

GitHub Actions automatically validates every push.

The workflow:

1. Starts PostgreSQL
2. Creates the database
3. Installs dependencies
4. Initializes test data
5. Executes the full pytest suite
6. Verifies coverage requirements

Workflow file:

```text
.github/workflows/tests.yml
```

Proof of successful CI execution is included in:

```text
actions_success.png
```

---

## Documentation

### Local Sphinx Build

Documentation source files are located in:

```text
docs/
```

Generate documentation locally:

```bash
cd docs
python -m sphinx -b html source build/html
```

Open:

```text
docs/build/html/index.html
```

### Read the Docs

Published documentation:

```text
https://zhk1127-jhu-software-concepts.readthedocs.io/en/latest/
```

The documentation includes:

* Architecture overview
* Data flow
* ETL layer
* Database layer
* Analysis layer
* Web layer
* Testing and CI
* Auto-generated API documentation from source code docstrings

---

## Screenshots

The screenshots directory contains examples of:

* SQL query output
* Flask dashboard
* Pull Data workflow
* Updated analytics results
* GitHub Actions execution
* Coverage reports

---

## Limitations

See:

```text
limitations.pdf
```

for discussion of limitations and potential biases in anonymously submitted admissions data.

---

## Deliverables Included

The following deliverables required by the assignment are included in this submission:

* GitHub repository (public)

* README.md

* requirements.txt

* coverage_summary.txt

* actions_success.png

* .github/workflows/tests.yml

* Sphinx-generated HTML documentation under `docs/build/html`

* Read the Docs deployment:

  https://zhk1127-jhu-software-concepts.readthedocs.io/en/latest/

* All required source files under `src/`

* All required pytest test files under `tests/`

* limitations.pdf

The GitHub Actions workflow successfully executes the complete pytest suite and verifies 100% test coverage. Documentation is generated with Sphinx and published through Read the Docs.



## Author

Hongkang Zhang

Johns Hopkins University

Software Concepts – Module 4
