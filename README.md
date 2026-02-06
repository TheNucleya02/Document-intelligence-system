# Document Intelligence System (Backend-First RAG)

A learning‑focused, production‑style GenAI backend for document Q&A. The UI is intentionally minimal (static HTML + Bootstrap) and serves only as an API client.

## Why This Structure
- Clear separation of **application code**, **runtime data**, and **infrastructure**
- Easy to reason about for recruiters and senior engineers
- GenAI/RAG architecture is front‑and‑center

## Folder Structure
```
app/                # Application source code 
  api/              # FastAPI routers
  core/             # config, logging, security
  services/         # ingestion, retrieval, llm
  db/               # ORM models + DB session
  schemas/          # request/response schemas
  static/           # minimal HTML UI
  main.py           # app entrypoint

data/               # Runtime data (gitignored)
  uploads/
  vector_store/
  samples/

scripts/            # One-off scripts
  migrate.py
  seed_data.py

infra/              # Docker and deployment assets
  Dockerfile
  docker-compose.yml

requirements.txt
README.md
ARCHITECTURE.md
postman_collection.json
```

## RAG Flow
```
Upload → Parse → Clean Text → Chunk → Embed → Store → Retrieve → Answer
```
Prompt structure is explicit:
1. Instruction
2. Retrieved chunks
3. Chat history
4. User question

RAG rules enforced:
- Never hallucinate
- Say “I don’t know” if answer isn’t in chunks
- Always cite document name + chunk index

## Run Locally (No Docker)
```bash
pip install -r requirements.txt
python scripts/migrate.py
uvicorn app.main:app --reload
```

UI pages:
- http://localhost:8000/login
- http://localhost:8000/register
- http://localhost:8000/upload
- http://localhost:8000/chat

## Run with Docker
```bash
echo "MISTRAL_API_KEY=your-key" > .env

docker compose -f infra/docker-compose.yml up --build
```

## API Endpoints
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /documents/upload`
- `GET /documents/list`
- `POST /chat/ask`
- `GET /chat/history?session_id=...`
- `GET /health`

## Example Data
- Example PDF: `data/samples/example.pdf`
- Seed user script: `scripts/seed_data.py`

```bash
python scripts/seed_data.py
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

## Minimal UI
No React/Vue/Next. The UI is static HTML + Bootstrap in `app/static` and uses `fetch` only.
