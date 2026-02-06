FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/data/uploads /app/data/vector_store
RUN chmod -R 777 /app/data

COPY app /app/app
COPY scripts /app/scripts
COPY requirements.txt /app/requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "pip install --no-cache-dir -r /app/requirements.txt && python /app/scripts/migrate.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
