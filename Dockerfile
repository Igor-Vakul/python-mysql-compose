# Base image: Python 3.12 on lightweight Debian
FROM python:3.12-slim

# Working directory inside the container
WORKDIR /app

# Copy dependencies first for layer caching.
# If requirements.txt hasn't changed, Docker won't reinstall packages.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . .

# Create a non-privileged user for security
RUN adduser --disabled-password --no-create-home appuser
USER appuser

# ARG — build-time variable, default 5000
ARG PORT=5000

# ENV — passes the value into the container at runtime
ENV APP_PORT=$PORT

EXPOSE $PORT

# Run with Gunicorn (production WSGI server)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$APP_PORT --workers 2 app:app"]
