# Spliits

A personal backend API built with FastAPI and PostgreSQL, fully containerized using Docker. The project also integrates Redis for JWT token revocation checks and Apache Airflow for ETL workflows.

This branch (`aws-deployment`) contains the specific configuration and architecture for deploying the application on AWS.

---

## AWS Deployment Architecture

- **Compute**: FastAPI and Redis run in Docker containers on an AWS EC2 instance (e.g., `t3.micro`).
- **Database**: PostgreSQL runs on AWS RDS (managed database), replacing the local Docker database containers (`db` and `airflow-db`).
- **Storage**: AWS S3 is used to store and serve user profile pictures publicly.
- **Permissions**: IAM roles attached to the EC2 instance are used for secure S3 access (no hardcoded keys in `.env`).

---

# Prerequisites

Before running this project, make sure you have the following installed or configured:

- Git
- Docker installed on the host machine (EC2 instance)
- AWS RDS (PostgreSQL 16) instance running in a VPC
- AWS S3 bucket configured for public read access
- AWS EC2 instance with an appropriate IAM role attached for S3 access

---

# Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/patrickbatman118-hub/projects1.git
cd projects1/spliits
git checkout aws-deployment
```

---

## 2. Configure Environment Variables

Create a `.env` file in the project root. Ensure you use your AWS RDS endpoints.

### API Database

```env
POSTGRES_USER=my_user
POSTGRES_PASSWORD=my_password
POSTGRES_DB=spliits

# Point this to your AWS RDS endpoint
DATABASE_URL=postgresql://my_user:my_password@<rds-endpoint>:5432/spliits

SECRET_KEY=my_secret_key
ALGORITHM=HS256
REDIS_HOST=redis
```

### Airflow Database (Optional)

```env
AIRFLOW_POSTGRES_USER=my_user
AIRFLOW_POSTGRES_PASSWORD=my_password
AIRFLOW_POSTGRES_DB=airflow

# Point this to your AWS RDS endpoint (ensure the airflow database is created)
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://my_user:my_password@<rds-endpoint>/airflow
```

---

## 3. Build and Start the Services

Build the containers and start the application.

```bash
docker compose up -d --build
```

This starts the following services:
- FastAPI API
- Redis

*Note: Airflow services are commented out by default in the `aws-deployment` branch because a `t3.micro` EC2 instance (1GB RAM) is not sufficient to run them alongside the API and Redis. A minimum of `t3.medium` is recommended if you wish to enable Airflow.*

---

## 4. Apply Database Migrations

Run the latest Alembic migrations against the RDS database. 

```bash
docker compose exec api uv run alembic upgrade head
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
| FastAPI API | `http://<ec2-public-ip>:8000` |
| Swagger UI | `http://<ec2-public-ip>:8000/docs` |
| ReDoc | `http://<ec2-public-ip>:8000/redoc` |

---

# AWS Specific Setup

## S3 Profile Pictures
User profile pictures are uploaded directly to an AWS S3 bucket.
- **Permissions**: The EC2 instance must have an IAM role attached with S3 access (e.g., an `AmazonS3FullAccess` policy or a restricted equivalent). This allows the FastAPI application's `boto3` client to upload and delete files without needing AWS access keys configured in the `.env` file.
- **Bucket Policy**: The bucket must have "Block all public access" turned off, and a bucket policy allowing `s3:GetObject` for `*` must be attached so images can be viewed publicly via their URL.

## Connecting to RDS PostgreSQL

To connect using DBeaver, pgAdmin, or another PostgreSQL client, you must connect from within the VPC (e.g., via the EC2 instance), as public access is typically disabled.
You can use SSH tunneling through your EC2 instance to access the RDS database from your local machine.

| Property | Value |
|----------|-------|
| Host | `<rds-endpoint>` |
| Port | 5432 |
| Username | Value from `.env` |
| Password | Value from `.env` |
| Database | `spliits` or `airflow` |

---

# Redis

Redis is used to cache revoked JWT tokens, allowing the API to validate revoked access tokens efficiently during authenticated requests.

Redis is available internally on the EC2 instance within the Docker network at `redis:6379`.

---

# Stopping the Project

Stop all running containers.

```bash
docker compose down
```
