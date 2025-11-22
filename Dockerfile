# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps (optional but safe for psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY app ./app
COPY app.py ./app.py

# Expose FastAPI port
EXPOSE 8000

# Default command: run Uvicorn with app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
