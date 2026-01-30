FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/uploads && mkdir -p /app/chroma_db
RUN chmod -R 777 /app/chroma_db /app/uploads

COPY backend/app /app/app
COPY backend/migrations.py /app/migrations.py
COPY .env /app/.env
COPY requirements.txt /app/requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "pip install --no-cache-dir -r /app/requirements.txt && python migrations.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
