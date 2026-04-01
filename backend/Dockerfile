# ── Backend Dockerfile ────────────────────────────────────────────────────────
#
# Builds a Django dev image.
# The Django development server is used intentionally for Week 1 — it
# auto-reloads on code changes without restarting the container.
# Replace with Gunicorn + Nginx for production.

FROM python:3.11-slim

# Prevents .pyc files from being written to disk — keeps the image clean.
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout/stderr — ensures log lines appear
# immediately in `docker-compose logs` without waiting for a flush.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so Docker can cache this layer.
# Only re-runs when requirements.txt changes, not on every code edit.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code.
COPY . .

# The container exposes port 8000; docker-compose maps it to the host.
EXPOSE 8000

# Wait for the database to be ready, run migrations, then start the dev server.
# Using 0.0.0.0 makes Django accessible from outside the container.
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
