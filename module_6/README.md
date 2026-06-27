# Module 6: RabbitMQ-Based Asynchronous Microservice Architecture

## Overview

Module 6 extends the GradCafe analytics platform by introducing an asynchronous microservice architecture using RabbitMQ. Instead of executing long-running tasks directly within the Flask application, the web service publishes tasks to a message queue and a dedicated worker service processes them asynchronously.

The system consists of four major services:

* **Web Service (Flask)**: User interface and task publisher
* **Worker Service**: Background task consumer and executor
* **RabbitMQ Service**: Message broker and task queue
* **PostgreSQL Service**: Persistent data storage

The architecture improves scalability, responsiveness, and separation of concerns. RabbitMQ decouples the web application from long-running data processing tasks, allowing the user interface to remain responsive while background jobs execute asynchronously.

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

## Quick Start

Clone the repository and start the complete microservice stack:

```bash
git clone https://github.com/zhk1127/jhu_software_concepts.git
cd jhu_software_concepts/module_6
docker compose up --build
```

The application will become available at:

* Flask Web Application: http://localhost:8080
* RabbitMQ Management Interface: http://localhost:15672

---

## Docker Images

The Module 6 Docker images have been published to Docker Hub.

### Web Service Image

```bash
docker pull zhk1127/module6-web:latest
```

### Worker Service Image

```bash
docker pull zhk1127/module6-worker:latest
```

Docker Hub repositories:

* https://hub.docker.com/r/zhk1127/module6-web
* https://hub.docker.com/r/zhk1127/module6-worker

---

## Running the Application

Start the entire microservice stack:

```bash
docker compose up --build
```

This command launches:

* PostgreSQL database
* RabbitMQ message broker
* Flask web service
* Background worker service
* Database initialization loader

---

## Application Access

### Flask Web Application

```
http://localhost:8080
```

Available actions:

* Pull Data
* Update Analysis
* View Analysis Results

### RabbitMQ Management Interface

```
http://localhost:15672
```

For educational and local development purposes, this project uses the default RabbitMQ credentials provided by the official Docker image:

```
Username: guest
Password: guest
```

---

## Asynchronous Task Processing

Two asynchronous tasks are implemented.

### Pull Data Task

When the user clicks **Pull Data**, the Flask application publishes:

```json
{
  "task": "scrape_new_data"
}
```

The worker service:

1. Receives the message
2. Executes the scraper
3. Cleans the data
4. Inserts records into PostgreSQL
5. Acknowledges the message

### Update Analysis Task

When the user clicks **Update Analysis**, the Flask application publishes:

```json
{
  "task": "recompute_analytics"
}
```

The worker service:

1. Receives the message
2. Recomputes analytical results
3. Updates cached analysis
4. Acknowledges the message

---

## Continuous Integration

GitHub Actions automatically performs:

* Dependency installation
* PostgreSQL initialization
* Unit testing with pytest
* Coverage verification
* Pylint quality checks

All Module 4, Module 5, and Module 6 GitHub Actions workflows completed successfully.

Current results:

* **Pytest:** 28 tests passed
* **Coverage:** 100%
* **Pylint:** 10.00/10

---

## Docker and Containerization

The application is implemented as a multi-container microservice architecture:

| Service    | Docker Image          | Responsibility                    |
| ---------- | --------------------- | --------------------------------- |
| Web        | module6-web           | User interface and task publisher |
| Worker     | module6-worker        | Background task execution         |
| RabbitMQ   | rabbitmq:3-management | Message broker                    |
| PostgreSQL | postgres:16           | Persistent storage                |

Docker Compose orchestrates the entire stack and automatically establishes networking between services.

---

## Notes

The RabbitMQ credentials (`guest/guest`) are used only for local development and demonstration purposes. Production deployments should use dedicated credentials and secret management solutions.
