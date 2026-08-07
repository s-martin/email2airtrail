FROM python:3.9-slim

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

CMD ["python", "daemon.py"]