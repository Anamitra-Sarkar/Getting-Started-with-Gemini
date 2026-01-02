FROM python:3.11-slim

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy backend code
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE ${PORT}

CMD ["/bin/sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT}"]
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY backend /app/backend
ENV PYTHONPATH=/app
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
