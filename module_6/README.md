# Module 6: RabbitMQ-Based Asynchronous Microservice Architecture

## Overview

Module 6 extends the GradCafe analytics platform by introducing an asynchronous microservice architecture using RabbitMQ. Instead of executing long-running tasks directly within the Flask web application, tasks are published to a RabbitMQ message queue and processed asynchronously by a dedicated worker service.

This architecture improves responsiveness, scalability, and separation of concerns by decoupling user interactions from computationally intensive background operations.

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
│   └── test_publisher.py
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

When the user clicks **Pull Data**, the web service publishes a message to RabbitMQ:

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
3. Updates cached analysis
4. Acknowledges the message

---

## Docker Images

The application images were successfully built, tagged, and published to Docker Hub.

### Web Service

```bash
docker pull zhk1127/module6-web:latest
```

Docker Hub:

```text
https://hub.docker.com/r/zhk1127/module6-web
```

---

### Worker Service

```bash
docker pull zhk1127/module6-worker:latest
```

Docker Hub:

```text
https://hub.docker.com/r/zhk1127/module6-worker
```

---

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

Final validation results:

| Validation            | Result          |
| --------------------- | --------------- |
| Pytest                | 30 tests passed |
| Coverage              | 100.00%         |
| Pylint                | 10.00 / 10      |
| Docker Compose        | Passed          |
| RabbitMQ Messaging    | Passed          |
| Docker Hub Publishing | Passed          |
| GitHub Actions        | Passed          |

---

## Docker Containers

| Service    | Image                 | Responsibility                    |
| ---------- | --------------------- | --------------------------------- |
| Web        | module6-web           | User interface and task publisher |
| Worker     | module6-worker        | Background task execution         |
| RabbitMQ   | rabbitmq:3-management | Message broker                    |
| PostgreSQL | postgres:16           | Persistent storage                |

Docker Compose automatically creates networking and service dependencies among all containers.

---

## Notes

* RabbitMQ uses durable queues and persistent messages.
* Worker consumers use `basic_qos(prefetch_count=1)`.
* Messages are acknowledged only after successful task completion.
* Docker images are publicly available on Docker Hub.
* The system was validated locally, through Docker Compose orchestration, and through GitHub Actions continuous integration.
