# GradCafe Analytics Dashboard (Module 5)

## Repository Information

GitHub Repository:

```text
https://github.com/zhk1127/jhu_software_concepts
```

GitHub SSH URL:

```text
git@github.com:zhk1127/jhu_software_concepts.git
```

Read the Docs:

```text
https://zhk1127-jhu-software-concepts.readthedocs.io/en/latest/
```

---

## Project Overview

This project analyzes GradCafe graduate admissions data using Flask and PostgreSQL. Module 5 extends the previous application by adding software assurance improvements, including environment-based database credentials, safer SQL construction, Pylint validation, and reproducible project setup.

The application supports:

1. Loading cleaned applicant records into PostgreSQL
2. Running SQL analytics queries
3. Displaying Q1–Q11 results in a Flask dashboard
4. Pulling additional GradCafe records
5. Updating analytics results from the web interface
6. Running pytest with 100% coverage
7. Running Pylint with a 10.00/10 score

---

## Environment Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Database credentials are loaded from environment variables rather than being hard-coded.

Create a local `.env` file using `.env.example` as a template:

```text
DB_NAME=gradcafe_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

The `.env` file is excluded from version control.

---

## PostgreSQL Setup

Create the database:

```sql
CREATE DATABASE gradcafe_db;
```

Load initial data:

```bash
python -m src.load_data
```

---

## Run Analytics Queries

```bash
python -m src.query_data
```

---

## Launch Flask App

```bash
python -m src.app
```

Open:

```text
http://127.0.0.1:5000/analysis
```

---

## Testing

Run all tests:

```bash
pytest
```

Current result:

```text
28 passed
Required test coverage of 100% reached.
Total coverage: 100.00%
```

---

## Pylint

Run Pylint on all source files:

```bash
pylint src
```

Verify the required score:

```bash
pylint src --fail-under=10
```

Current result:

```text
Your code has been rated at 10.00/10
```

Pylint is configured through the included `.pylintrc` file.

---

## SQL Injection Defenses

Module 5 removes unsafe SQL string construction where dynamic SQL was needed. SQL queries use PostgreSQL parameterization and psycopg SQL composition where appropriate. Database credentials are no longer hard-coded and are loaded from environment variables.

---

## Continuous Integration

GitHub Actions is included under:

```text
.github/workflows/
```

The workflow validates project setup, tests, and code quality checks.

---

## Key Deliverables

This Module 5 submission includes:

* `src/`
* `tests/`
* `requirements.txt`
* `.env.example`
* `.gitignore`
* `.pylintrc`
* `.github/workflows/`
* `README.md`
* `coverage_summary.txt`
* screenshots
* Sphinx documentation source files

---

## Author

Hongkang Zhang
Johns Hopkins University
Software Concepts – Module 5
