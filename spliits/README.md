
```markdown
# Spliits

A FastAPI/Python API with a PostgreSQL database, completely containerized with Docker.

## Prerequisites

Before running this project, make sure you have the following installed:
* [Git](https://git-scm.com/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)

---

## Getting Started

### 1. Clone the Repository
Open your terminal and run:
```bash
git clone https://github.com/patrickbatman118-hub/projects1/tree/master/spliits
cd spliits

```

### 2. Configure Environment Variables

Create a `.env` file in the root directory of the project and add your database configuration:

```env
POSTGRES_USER=my_user
POSTGRES_PASSWORD=my_password
POSTGRES_DB=my_database
DATABASE_URL=postgresql://myuser:mypassword@db:5432/mydatabase
SECRET_KEY=my_secret_key
ALGORITHM=my_algorithm

```

### 3. Start the Application

Run Docker Compose to build and start the API and database in the background:

```bash
docker compose up -d --build

```

*Note: The API will wait to start until the database health check passes.*

### 4. Verify It's Running

Check the status of your containers:

```bash
docker compose ps

```

You should see both the `api` and `db` services marked as `running` (and the db as `healthy`). You can access the API locally at `http://localhost:8000`.

---

## Connecting a Database GUI (DBeaver / pgAdmin)

To view the database using an external GUI tool, use the following connection settings:

* **Host:** `localhost`
* **Port:** `5434`  *(Note: This maps to internal port 5432)*
* **Username:** `myuser` (or whatever you set in `.env`)
* **Password:** `mypassword` (or whatever you set in `.env`)
* **Database:** `mydatabase` (or whatever you set in `.env`)

---

## Stopping the Project

To stop the containers and free up your system ports without deleting your database data:

```bash
docker compose down

```

```

```