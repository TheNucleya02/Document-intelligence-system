
# PDF Q&A Application

A document question-answering system built with FastAPI backend and Streamlit frontend.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file with:
   ```
   ASTRA_DB_API_ENDPOINT=your_astra_db_endpoint
   ASTRA_DB_APPLICATION_TOKEN=your_astra_db_token
   MISTRAL_API_KEY=your_mistral_api_key
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

   Or run manually:
   ```bash
   # Terminal 1 - Backend
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2 - Frontend  
   streamlit run frontend/app.py --server.port 8501
   ```

## Features

-  Upload PDF and DOCX documents
- 🤖 AI-powered question answering using Mistral AI
- 💾 Vector storage with AstraDB
- 💬 Conversational chat with memory
- 🎨 Clean Streamlit interface

## API Endpoints

- `GET /` - Health check
- `GET /health` - Backend status
- `POST /upload-documents` - Upload and process documents
- `POST /ask-question` - Ask questions about documents
- `GET /collections` - List available collections

## Project Structure

