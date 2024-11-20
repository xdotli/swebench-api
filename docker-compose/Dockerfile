FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Docker (needed for SWE-bench evaluation)
RUN curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh

# Set working directory
WORKDIR /app

# Clone OpenHands repository
RUN git clone https://github.com/All-Hands-AI/OpenHands.git .

# Replace poetry.lock and pyproject.toml with updated versions
COPY poetry.lock /app/poetry.lock
COPY pyproject.toml /app/pyproject.toml

# Install Python dependencies
RUN pip install openhands-aci
RUN pip install -e .[inference]

# Copy configuration files
COPY config.toml /app/config.toml


# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

RUN poetry install

ENTRYPOINT ["/app/entrypoint.sh"] 
