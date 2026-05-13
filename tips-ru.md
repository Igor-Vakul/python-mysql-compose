# Python + MySQL + Docker Compose — Пошаговое руководство

## Шаг 1 — Создай файлы проекта

Создай `app.py`, `templates/index.html`, `requirements.txt` с зависимостями `flask`, `mysql-connector-python`, `python-dotenv`, `gunicorn`.

```
pip install -r requirements.txt
```

---

## Шаг 2 — Запусти локально

Запусти приложение локально, чтобы проверить что оно работает до Docker.

```
python app.py
```

---

## Шаг 3 — Запусти MySQL в Docker

Запусти контейнер MySQL с переменными окружения, volume и проброском порта.

```
docker run --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=1 \
  -e MYSQL_DATABASE=mydb \
  -v mysql-data:/var/lib/mysql \
  -p 3306:3306 \
  -d mysql:8
```

---

## Шаг 4 — Создай .env и подключись к MySQL

Создай файл `.env` с данными подключения. Используй `python-dotenv` для загрузки переменных в `app.py`.

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

## Шаг 5 — Создай Dockerfile

Собери Docker образ для Python приложения на основе `python:3.12-slim`.

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

## Шаг 6 — Собери Docker образ

Собери образ и проверь что он создался.

```
docker build -t dinner_py-mysql:v0.1 .
docker images
```

---

## Шаг 7 — Создай сеть и запусти контейнеры

Создай Docker сеть чтобы контейнеры могли общаться по имени. В качестве `MYSQL_HOST` используй имя контейнера MySQL (`mysql-db`), а не `localhost`.

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

## Шаг 8 — Останови и удали контейнеры

```
docker rm -f dinner_py mysql-db
```

---

## Шаг 9 — Создай docker-compose.yml

Опиши все сервисы в одном файле. Используй `healthcheck` чтобы приложение дождалось готовности MySQL.

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

## Шаг 10 — Запушь на GitHub

Создай `.gitignore` чтобы исключить `.env` и `__pycache__`, затем закоммить и запушь.

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

## Отличия Node.js от Python

| | Node.js | Python |
|---|---|---|
| Файл зависимостей | `package.json` | `requirements.txt` |
| Установка | `npm install` | `pip install -r requirements.txt` |
| Библиотека БД | `mysql2` | `mysql-connector-python` |
| Веб-фреймворк | `express` | `flask` |
| Продакшен сервер | node | `gunicorn` |
| Переменные окружения | `dotenv` | `python-dotenv` |
| Запуск | `node index.js` | `python app.py` |
