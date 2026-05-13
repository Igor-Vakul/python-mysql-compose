# Python + MySQL + Docker Compose — Step by Step Guide

## Step 1 — Create project files

Create `app.py`, `templates/index.html`, `requirements.txt` with `flask`, `mysql-connector-python`, `python-dotenv`, `gunicorn`.

```
pip install -r requirements.txt
```

---

## Step 2 — Run locally

Run the app locally to verify it works before adding Docker.

```
python app.py
```

---

## Step 3 — Run MySQL in Docker

Run a MySQL container with environment variables, volume and port mapping.

```
docker run --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=1 \
  -e MYSQL_DATABASE=mydb \
  -v mysql-data:/var/lib/mysql \
  -p 3306:3306 \
  -d mysql:8
```

---

## Step 4 — Create .env and connect to MySQL

Create a `.env` file with database credentials. Use `python-dotenv` to load them in `app.py`.

```
MYSQL_HOST=localhost
MYSQL_USERNAME=root
MYSQL_PASSWORD=1
MYSQL_DATABASE=mydb
```

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Step 5 — Create Dockerfile

Build a Docker image for the Python app using `python:3.12-slim` as base image.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN adduser --disabled-password --no-create-home appuser
USER appuser
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
```

---

## Step 6 — Build Docker image

Build the image and verify it was created.

```
docker build -t dinner_py-mysql:v0.1 .
docker images
```

---

## Step 7 — Create network and run containers

Create a Docker network so containers can communicate by container name. Use the MySQL container name as `MYSQL_HOST`.

```
docker network create dinner_py-mysql

docker run --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=1 \
  -e MYSQL_DATABASE=mydb \
  -v mysql-data:/var/lib/mysql \
  -p 3306:3306 \
  --network dinner_py-mysql \
  -d mysql:8

docker run -d -p 5000:5000 --name dinner_py \
  -e MYSQL_HOST=mysql-db \
  -e MYSQL_USERNAME=root \
  -e MYSQL_PASSWORD=1 \
  -e MYSQL_DATABASE=mydb \
  --network dinner_py-mysql \
  dinner_py-mysql:v0.1
```

---

## Step 8 — Stop and remove containers

```
docker rm -f dinner_py mysql-db
```

---

## Step 9 — Create docker-compose.yml

Describe all services in one file. Use `healthcheck` so the app waits for MySQL to be ready.

```yaml
services:
  mysql-db:
    image: mysql:8
    container_name: mysql-db
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=1
      - MYSQL_DATABASE=mydb
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 10s
      retries: 5

  python-app:
    build: .
    image: dinner_py-mysql:v0.1
    container_name: python-app
    depends_on:
      mysql-db:
        condition: service_healthy
    ports:
      - "5000:5000"
    environment:
      - MYSQL_HOST=mysql-db
      - MYSQL_USERNAME=root
      - MYSQL_PASSWORD=1
      - MYSQL_DATABASE=mydb

  phpmyadmin:
    image: phpmyadmin/phpmyadmin
    container_name: phpmyadmin
    depends_on:
      mysql-db:
        condition: service_healthy
    ports:
      - "8080:80"
    environment:
      - PMA_HOST=mysql-db
      - PMA_USER=root
      - PMA_PASSWORD=1

volumes:
  mysql-data:
```

```
docker compose up -d
docker compose down
```

---

## Step 10 — Push to GitHub

Create `.gitignore` to exclude `.env` and `__pycache__`, then commit and push.

```
# .gitignore
.env
__pycache__
```

```
git add .
git commit -m "initial commit"
git push
```

---

## Key differences: Node.js vs Python

| | Node.js | Python |
|---|---|---|
| Package file | `package.json` | `requirements.txt` |
| Install | `npm install` | `pip install -r requirements.txt` |
| DB library | `mysql2` | `mysql-connector-python` |
| Web framework | `express` | `flask` |
| Production server | node | `gunicorn` |
| Env vars | `dotenv` | `python-dotenv` |
| Run | `node index.js` | `python app.py` |
