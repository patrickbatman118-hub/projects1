# Spliits

A personal backend API built with FastAPI and PostgreSQL, fully containerized using Docker. The project also integrates Redis for JWT token revocation checks and Apache Airflow for ETL workflows.

---

# Prerequisites

Before running this project, make sure you have the following installed:

- Git
- Docker Desktop (includes Docker Compose)

---

# Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/patrickbatman118-hub/projects1.git
cd projects1/spliits
```

---

## 2. Configure Environment Variables

Create a `.env` file in the project root and configure the required environment variables.

### API Database

```env
POSTGRES_USER=my_user
POSTGRES_PASSWORD=my_password
POSTGRES_DB=my_database

DATABASE_URL=postgresql://my_user:my_password@db:5432/my_database
DATABASE_URL1=postgresql://my_user:my_password@db:5432/my_database

SECRET_KEY=my_secret_key
ALGORITHM=HS256
```

### Airflow Database

```env
AIRFLOW_POSTGRES_USER=airflow
AIRFLOW_POSTGRES_PASSWORD=airflow
AIRFLOW_POSTGRES_DB=airflow

AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@airflow-db/airflow
```

### Airflow Admin

```env
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=admin
AIRFLOW_ADMIN_EMAIL=admin@example.com
AIRFLOW_ADMIN_FIRSTNAME=Admin
AIRFLOW_ADMIN_LASTNAME=User
```

---

## 3. Build and Start the Services

Build all containers and start the application.

```bash
docker compose up -d --build
```

This starts the following services:

- FastAPI API
- PostgreSQL
- Redis
- Airflow PostgreSQL
- Airflow Initialization
- Airflow Scheduler
- Airflow Webserver

The API automatically waits until the PostgreSQL database is healthy before starting.

---

## 4. Apply Database Migrations

Run the latest Alembic migrations.

```bash
docker compose exec api alembic upgrade head
```

---

## 5. Verify Everything is Running

```bash
docker compose ps
```

---

# Available Services

| Service | URL |
|----------|-----|
| FastAPI API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Airflow Web UI | http://localhost:8080 |

---

# Connecting to PostgreSQL

To connect using DBeaver, pgAdmin, or another PostgreSQL client:

| Property | Value |
|----------|-------|
| Host | localhost |
| Port | 5433 |
| Username | Value from `.env` |
| Password | Value from `.env` |
| Database | Value from `.env` |

---

# Redis

Redis is used to cache revoked JWT tokens, allowing the API to validate revoked access tokens efficiently during authenticated requests.

Redis is available on:

```
localhost:6379
```

---

# Apache Airflow

Apache Airflow is used for ETL workflows.

The Airflow web interface is available at:

```
http://localhost:8080
```

---

# Stopping the Project

Stop all running containers.

```bash
docker compose down
```

Database volumes are preserved, so your data will remain available the next time you start the project.

---

# Rebuilding the Containers

If you modify dependencies or the Docker configuration, rebuild the containers with:

```bash
docker compose up -d --build
```