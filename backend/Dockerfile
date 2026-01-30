FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app/app
COPY ./migrations.py /app/migrations.py
COPY .env /app/.env

RUN mkdir -p /app/uploads && mkdir -p /app/chroma_db
RUN chmod -R 777 /app/chroma_db /app/uploads

EXPOSE 8000

CMD ["sh", "-c", "python migrations.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]