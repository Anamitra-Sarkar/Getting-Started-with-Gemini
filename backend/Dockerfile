FROM python:3.12-slim

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy backend code
COPY . /app/backend

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8000

EXPOSE ${PORT}

CMD ["/bin/sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT}"]

