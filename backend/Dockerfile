FROM python:3.10-slim

WORKDIR /code

# Install Tesseract and Poppler (required for pdf2image)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY .env /code/.env

RUN mkdir -p /code/uploads && mkdir -p /code/chroma_db

# Create the directories explicitly
RUN mkdir -p /code/chroma_db /code/uploads

# Grant permissions (brute force for safety in containers)
RUN chmod -R 777 /code/chroma_db /code/uploads

# GOOD - SQLite requires a single writer
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]