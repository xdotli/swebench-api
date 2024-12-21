FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory with proper permissions
RUN mkdir -p /app/cache && chmod 777 /app/cache

# Create docker socket directory
RUN mkdir -p /var/run && chmod 777 /var/run

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]