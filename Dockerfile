FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY config.py daemon.py ./
COPY pattern/ ./pattern/

# Create the logs directory
RUN mkdir -p logs

# Load environment variables
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 \
    CMD test -f /app/logs/daemon.log || exit 1

CMD ["python", "daemon.py"]
