# Module 6: RabbitMQ-Based Asynchronous Microservice Architecture

## Overview

Module 6 extends the GradCafe analytics platform by introducing an asynchronous microservice architecture using RabbitMQ. Instead of executing long-running tasks directly within the Flask web application, tasks are published to a RabbitMQ message queue and processed asynchronously by a dedicated worker service.

This architecture improves responsiveness, scalability, fault tolerance, and separation of concerns by decoupling user interactions from computationally intensive background operations.

The system consists of four primary services:

* **Web Service (Flask)**: User interface and task publisher
* **Worker Service**: Background task consumer and executor
* **RabbitMQ Service**: Message broker and task queue
* **PostgreSQL Service**: Persistent data storage

---

## Microservice Architecture

```text
                    Browser
                        |
                        V
              Flask Web Service
                  (module6-web)
                        |
                        V
                 RabbitMQ Queue
                        |
                        V
                 Worker Service
                (module6-worker)
                        |
                        V
                PostgreSQL Database
```

---

## Project Structure

```text
module_6/

├── docker-compose.yml
├── README.md
├── .pylintrc
├── setup.py
├── pytest.ini
├── .env.example
├── static/
├── templates/
├── docs/
├── tests/
│   ├── test_analysis_format.py
│   ├── test_buttons.py
│   ├── test_db_insert.py
│   ├── test_flask_page.py
│   ├── test_integration_end_to_end.py
│   ├── test_publisher.py
|   ├── test_clean.py
|   ├── test_scrape.py
|   └── test_pull_new_data_transaction.py
│
├── src/
│   ├── data/
│   │   └── cleaned_applicant_data.json
│   │
│   ├── db/
│   │   └── load_data.py
│   │
│   ├── web/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── run.py
│   │   ├── publisher.py
│   │   └── app/
│   │       └── app.py
│   │
│   └── worker/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── consumer.py
│       └── etl/
│           ├── pull_new_data.py
│           ├── clean.py
│           ├── scrape.py
│           └── query_data.py
```

---

## Local Python Environment (Optional)

For local development and testing, a Python virtual environment can be created as follows:

```bash
python -m venv .venv

# Windows
source .venv/Scripts/activate

# Linux/macOS
source .venv/bin/activate

pip install pytest pytest-cov pylint
pip install -r src/web/requirements.txt
pip install -r src/worker/requirements.txt
```

The `.venv` directory is intentionally excluded from the repository. All required dependencies are specified in the requirements files and can be recreated automatically.

For final validation and deployment, Docker Compose is the recommended and reference execution environment.

---

## Quick Start

Clone the repository:

```bash
git clone https://github.com/zhk1127/jhu_software_concepts.git
cd jhu_software_concepts/module_6
```

Build and launch the complete microservice stack:

```bash
docker compose up --build
```

---

## Services

The Docker Compose configuration launches:

* PostgreSQL database service
* RabbitMQ message broker
* Flask web service
* Background worker service
* One-time database initialization loader

Verify running services:

```bash
docker compose ps
```

---

## Application Access

### Flask Web Application

```text
http://localhost:8080
```

Available actions:

* Pull Data
* Update Analysis
* View Analysis Results

---

### RabbitMQ Management Interface

```text
http://localhost:15672
```

Credentials:

```text
Username: guest
Password: guest
```

These credentials are used only for local development and demonstration purposes.

---

## Asynchronous Task Processing

### Pull Data Task

When the user clicks **Pull Data**, the web service publishes:

```json
{
  "task": "scrape_new_data"
}
```

The worker service:

1. Consumes the message
2. Executes the scraper
3. Cleans the data
4. Inserts records into PostgreSQL
5. Acknowledges the message

---

### Update Analysis Task

When the user clicks **Update Analysis**, the web service publishes:

```json
{
  "task": "recompute_analytics"
}
```

The worker service:

1. Consumes the message
2. Recomputes analytical results
3. Refreshes analytics using the latest PostgreSQL state
4. Acknowledges the message

---

## Incremental Loading and Idempotent Updates

To support reliable asynchronous ingestion, Module 6 implements an incremental loading mechanism using a PostgreSQL `ingestion_watermarks` table.

### Watermark Tracking

The `ingestion_watermarks` table stores the latest successfully processed position for each data source:

```sql
CREATE TABLE ingestion_watermarks (
    source TEXT PRIMARY KEY,
    last_seen INTEGER NOT NULL
);
```

During each `scrape_new_data` task:

1. The worker reads the current watermark from PostgreSQL.
2. The scraper calculates the next GradCafe page to process.
3. New records are scraped and cleaned.
4. Records are inserted into PostgreSQL.
5. After successful insertion, the watermark is advanced.

This mechanism enables incremental processing and prevents unnecessary reprocessing of previously ingested records.

### Idempotent Inserts

To guarantee idempotent behavior, PostgreSQL inserts use:

```sql
ON CONFLICT DO NOTHING
```

This ensures that duplicate records are safely ignored and repeated task execution does not create duplicate database entries.

### Analytics Updates

The `recompute_analytics` task is also processed asynchronously through RabbitMQ. The worker recomputes analytical summaries, and the Flask UI displays analytics generated from the latest PostgreSQL-backed state.

---

## Docker Images

The application images were successfully built, tagged, and published to a public Docker Hub repository named `module_6`.

### Docker Hub Repository

```text
https://hub.docker.com/r/zhk1127/module_6
```

### Pull the Web Service Image

```bash
docker pull zhk1127/module_6:web
```

### Pull the Worker Service Image

```bash
docker pull zhk1127/module_6:worker
```

### Inspect Available Image Tags

```bash
docker pull zhk1127/module_6:web
docker pull zhk1127/module_6:worker
```

The Docker Hub repository contains two published images:

| Tag      | Description                                     |
| -------- | ----------------------------------------------- |
| `web`    | Flask web service and RabbitMQ publisher        |
| `worker` | RabbitMQ consumer and background task processor |

### Run the Complete Application Stack

The recommended deployment method is Docker Compose:

```bash
git clone https://github.com/zhk1127/jhu_software_concepts.git
cd jhu_software_concepts/module_6
docker compose up --build
```

After startup, the following services become available:

| Service                | URL                    |
| ---------------------- | ---------------------- |
| Flask Web Application  | http://localhost:8080  |
| RabbitMQ Management UI | http://localhost:15672 |

RabbitMQ credentials:

```text
Username: guest
Password: guest
```

The Docker Hub repository is provided both to satisfy the image publishing requirement and to allow independent inspection and execution of the web and worker microservices.

## Continuous Integration

GitHub Actions automatically perform:

* Dependency installation
* PostgreSQL initialization
* Unit testing
* Coverage validation
* Pylint quality checks

All Module 4, Module 5, and Module 6 GitHub Actions workflows completed successfully.

---

## Validation Results

| Validation            | Result          |
| --------------------- | --------------- |
| Pytest                | 57 tests passed |
| Coverage              | 100.00%         |
| Pylint                | 10.00 / 10      |
| Docker Compose        | Passed          |
| RabbitMQ Messaging    | Passed          |
| Docker Hub Publishing | Passed          |
| GitHub Actions        | Passed          |
---

## Docker Containers

| Service    | Image                    | Responsibility                    |
| ---------- | ------------------------ | --------------------------------- |
| Web        | zhk1127/module_6:web     | User interface and task publisher |
| Worker     | zhk1127/module_6:worker  | Background task execution         |
| RabbitMQ   | rabbitmq:3-management    | Message broker                    |
| PostgreSQL | postgres:16              | Persistent storage                |
Docker Compose automatically creates networking and service dependencies among all containers.

---

## Notes

* RabbitMQ uses durable queues and persistent messages.
* Worker consumers use `basic_qos(prefetch_count=1)`.
* Messages are acknowledged only after successful task completion.
* PostgreSQL uses incremental ingestion watermarks.
* Database inserts are idempotent via `ON CONFLICT DO NOTHING`.
* Docker images are publicly available on Docker Hub.
* The system was validated locally, through Docker Compose orchestration, and through GitHub Actions continuous integration.
* The duplicate-code pylint rule was disabled because independent microservices (web, worker, and database modules) intentionally maintain separate database configuration blocks. Enabling this rule reduces the score from 10.00 to 9.97 due solely to repeated configuration definitions rather than duplicated business logic.