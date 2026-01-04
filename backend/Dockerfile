FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for reportlab and Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# copy requirements from repository root and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy backend code to /app/backend
COPY backend /app/backend

# create writable directory for SQLite database
# Using 755 instead of 777 for better security - owner can write, others can read/execute
RUN mkdir -p /app/data && chmod 755 /app/data

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8000
ENV DATABASE_URL=sqlite:///./data/backend_data.db

EXPOSE ${PORT}

# Use exec form for proper signal handling
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT}"]
