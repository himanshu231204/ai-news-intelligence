# Production Dockerfile for AI News Agent
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY main.py .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Create data directories
RUN mkdir -p /app/chroma_data /app/logs

# Default: run as scheduler
ENV MODE=scheduler
ENV LOG_LEVEL=INFO

CMD ["python", "main.py", "--mode", "${MODE}"]
