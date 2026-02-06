# Document Intelligence System (Minimal RAG Backend)

A learning-focused, production-style Document Intelligence backend with a minimal HTML UI. The system ingests PDFs/DOCX, creates deterministic chunks + embeddings, and answers questions with strict source attribution.

## Goals
- Stable, testable ingestion pipeline
- Clear RAG flow with explicit prompt structure
- DB-backed chat sessions and message history
- Minimal frontend (HTML + Bootstrap + vanilla JS)

## Stack
- FastAPI + SQLAlchemy
- PostgreSQL (Docker) or SQLite (local)
- Chroma DB (local embeddings store)
- Mistral AI (LLM + embeddings)

## Quick Start

### Docker
```bash
echo "MISTRAL_API_KEY=your-key" > .env
docker-compose up --build
```

- UI: http://localhost:8000/login
- API Docs: http://localhost:8000/docs

### Local (no Docker)
```bash
cd backend
pip install -r ../requirements.txt
python migrations.py
uvicorn app.main:app --reload
```

## Minimal UI Pages
- `/login`
- `/register`
- `/upload`
- `/chat`

The UI is a thin API client with no build tools or frameworks.

## API Endpoints

**Auth**
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`

**Documents**
- `POST /documents/upload`
- `GET /documents/list`

**Chat**
- `POST /chat/ask`
- `GET /chat/history?session_id=...`

**Health**
- `GET /health`

## RAG Flow (Deterministic)
```
Upload → Parse → Clean Text → Chunk → Embed → Store → Retrieve → Answer
```

Prompt structure is explicit and always includes:
1. Instruction
2. Retrieved chunks
3. Chat history
4. User question

RAG rules enforced in the system prompt:
- Never hallucinate
- Say “I don’t know” if answer is not in chunks
- Always cite document name + chunk index

## Database Schema
Tables:
- `users`
- `documents`
- `document_chunks`
- `chat_sessions`
- `chat_messages`

Each chunk stores:
- `document_id`, `user_id`, `page_number`, `chunk_index`, `text`

## Example PDF + Seed Data
- Example PDF: `backend/sample_data/example.pdf`
- Seed user script: `backend/seed_data.py`

```bash
cd backend
python seed_data.py
```

## Example cURL

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo-password"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo-password"}'

# Upload
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@backend/sample_data/example.pdf"

# Ask
curl -X POST http://localhost:8000/chat/ask \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this document about?"}'
```

## Environment Variables
```env
DATABASE_URL=postgresql://user:password@localhost:5432/document_intelligence
SECRET_KEY=your-secret-key-change-in-production
MISTRAL_API_KEY=your-mistral-key
LLM_MODEL=mistral-large-latest
EMBEDDING_MODEL=mistral-embed
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_K=4
```

## Folder Structure (Key)
```
backend/app/api            # FastAPI routers
backend/app/core           # auth, config, logging
backend/app/services       # ingestion, retrieval, llm
backend/app/static         # minimal UI
backend/sample_data        # example PDF
```
