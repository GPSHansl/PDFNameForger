FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip for better package resolution
RUN pip install --upgrade pip

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Mount volumes
VOLUME ["/app/scripts", "/app/config", "/app/input", "/app/output"]

# Set the entrypoint to the main script
ENTRYPOINT ["python", "/app/scripts/main.py"]
