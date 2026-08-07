FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy configuration and script
COPY config.py daemon.py .env ./

# Copy the patterns directory
COPY patterns/ ./patterns/

# Create the logs directory
RUN mkdir -p logs

# Load environment variables
ENV PYTHONUNBUFFERED=1

CMD ["python", "daemon.py"]