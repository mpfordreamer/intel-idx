# ==============================================================================
# IDX-Intel AI — Enterprise Corporate Action Intelligence Bot Dockerfile
# ==============================================================================
FROM python:3.11-slim

# Set environment variables for Python runtime optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies required for asyncpg, PostgreSQL, and network checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 --upgrade pip && \
    pip install --no-cache-dir --default-timeout=100 -r requirements.txt && \
    playwright install chromium --with-deps

# Copy application code, migrations, static assets, and configurations
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini .
COPY pyproject.toml .

# Expose port 8002 for FastAPI server
EXPOSE 8002

# Entrypoint: Run Alembic migrations automatically on boot, then start Uvicorn
CMD sh -c "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8002"
