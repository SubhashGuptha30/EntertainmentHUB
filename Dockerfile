# ── Entertainment Hub — Cloud Run Dockerfile ─────────────────────────
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr (important for Cloud Run logs)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run sets the PORT env var (default 8080)
# Use 2 workers + 4 threads for a lightweight container
CMD exec gunicorn --bind :${PORT:-8080} --workers 2 --threads 4 --timeout 120 app:app
