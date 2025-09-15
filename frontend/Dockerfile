# Frontend/Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Create Streamlit config directory
RUN mkdir -p /home/appuser/.streamlit

# Create Streamlit configuration
RUN echo "[server]" > /home/appuser/.streamlit/config.toml \
    && echo "address = '0.0.0.0'" >> /home/appuser/.streamlit/config.toml \
    && echo "port = 8501" >> /home/appuser/.streamlit/config.toml \
    && echo "headless = true" >> /home/appuser/.streamlit/config.toml \
    && echo "enableCORS = false" >> /home/appuser/.streamlit/config.toml \
    && echo "enableXsrfProtection = false" >> /home/appuser/.streamlit/config.toml

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "app.py"]