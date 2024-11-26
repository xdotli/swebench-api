FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Create cache directory with proper permissions 
RUN mkdir -p /app/cache && chmod 777 /app/cache

# Create docker socket directory with proper permissions
RUN mkdir -p /var/run && chmod 777 /var/run

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app ./app

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]