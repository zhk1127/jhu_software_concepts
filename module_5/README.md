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

This project analyzes GradCafe graduate admissions data using Flask and PostgreSQL. Module 5 extends the previous application by adding software assurance and security improvements, including environment-based database credentials, SQL injection defenses, dependency analysis, GitHub Actions continuous integration, and reproducible project setup.

The application supports:

1. Loading cleaned applicant records into PostgreSQL
2. Running SQL analytics queries (Q1–Q11)
3. Displaying analytics results through a Flask dashboard
4. Pulling additional GradCafe records
5. Updating analytics results from the web interface
6. Running automated tests with 100% coverage
7. Running Pylint with a 10.00/10 score
8. Generating dependency graphs
9. Performing dependency security scanning with Snyk

---

# Environment Setup

## Option 1: Standard Python venv

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install the project package:

```bash
pip install -e .
```

---

## Option 2: Using uv

Install uv:

```bash
pip install uv
```

Create a virtual environment:

```bash
uv venv
source .venv/Scripts/activate
```

Install dependencies:

```bash
uv pip install -r requirements.txt
```

Install the package:

```bash
uv pip install -e .
```

---

# Environment Variables

Database credentials are loaded from environment variables rather than being hard-coded.

Create a local `.env` file using `.env.example` as a template:

```text
DB_NAME=gradcafe_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

The `.env` file is excluded from version control through `.gitignore`.

---

# PostgreSQL Setup

Create the database:

```sql
CREATE DATABASE gradcafe_db;
```

Load initial data:

```bash
python -m src.load_data
```

---

# Running Analytics Queries

Execute all analytical queries:

```bash
python -m src.query_data
```

---

# Launch Flask Application

Start the Flask application:

```bash
python -m src.app
```

Open the dashboard:

```text
http://127.0.0.1:5000/analysis
```

---

# Testing

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

# Pylint

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

Pylint configuration is stored in:

```text
.pylintrc
```

---

# Dependency Graph Analysis

Generate the dependency graph:

```bash
pydeps src/app.py --noshow -T svg -o dependency.svg
```

The generated `dependency.svg` visualizes relationships among project modules and external dependencies.

---

# SQL Injection Defenses

Module 5 refactors dynamic SQL usage to follow secure database programming practices.

Security improvements include:

* No SQL built using f-strings
* No SQL built using string concatenation
* No SQL built using `.format()`
* psycopg SQL composition for dynamic SQL fragments
* Parameterized query execution using `cursor.execute(stmt, params)`
* Separation of SQL construction and execution
* Query LIMIT enforcement
* Environment-based credential management

These changes prevent user input from being interpreted as executable SQL code.

---

# Database Hardening

Database credentials are stored in environment variables and are not committed to source control.

The application loads configuration from `.env` files using `python-dotenv`.

Sensitive information is excluded from Git tracking through `.gitignore`.

---

# Dependency Security Scanning

Run Snyk dependency scanning:

```bash
snyk test
```

Current result:

```text
Tested 50 dependencies for known issues.
No vulnerable paths found.
```

Snyk verifies that project dependencies do not contain known security vulnerabilities.

---

Additional static application security testing was performed using Snyk Code.

# Continuous Integration

GitHub Actions workflows are located under:

```text
.github/workflows/
```

The CI pipeline automatically performs:

* Pytest execution
* Coverage verification
* Pylint validation (`--fail-under=10`)
* Dependency graph generation
* Snyk dependency scanning

Every push automatically triggers validation of project quality and security checks.

---

# Package Installation

The project can be installed as an editable Python package:

```bash
pip install -e .
```

or

```bash
uv pip install -e .
```

Editable installation allows source code modifications to be immediately reflected without reinstalling the package.

---

# Key Deliverables

This Module 5 submission includes:

* `src/`
* `tests/`
* `requirements.txt`
* `setup.py`
* `.env.example`
* `.gitignore`
* `.pylintrc`
* `.github/workflows/`
* `README.md`
* `coverage_summary.txt`
* `dependency.svg`
* Snyk analysis screenshots
* Sphinx documentation source files
* Read the Docs configuration

---

# Security Features Summary

Module 5 introduces the following software assurance improvements:

* Environment-based credential management
* SQL injection defenses
* Query LIMIT enforcement
* Dependency graph generation
* Pylint static analysis
* Snyk dependency scanning
* GitHub Actions CI validation
* Reproducible installation using pip and uv

---

## Author

Hongkang Zhang

Johns Hopkins University

Software Concepts – Module 5
