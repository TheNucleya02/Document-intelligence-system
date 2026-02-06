# Architecture

## Overview
Backend‑first RAG system with a minimal static UI. The backend owns ingestion, retrieval, and chat memory. The UI is a thin API client.

## Application Layout
- `app/api`: FastAPI routes
- `app/core`: config, logging, auth
- `app/services`: ingestion, retrieval, LLM, vector store
- `app/db`: SQLAlchemy models + session
- `app/schemas`: request/response models
- `app/static`: HTML UI

## Data & Runtime
- `data/uploads`: uploaded files
- `data/vector_store`: Chroma persistence
- `data/samples`: sample docs (local only)

## RAG Pipeline
```
Upload → Parse → Clean → Chunk → Embed → Store → Retrieve → Answer
```

## LLM Prompt Structure
The LLM receives:
1. Instruction
2. Retrieved chunks
3. Chat history
4. User question

Rules:
- Use only retrieved chunks
- If not present, respond “I don’t know”
- Always cite document name + chunk index

## Persistence
- `document_chunks` stores chunk metadata
- `chat_sessions` binds a session to a document set
- `chat_messages` stores conversation history and sources

## Observability
Structured logs include `request_id`, `user_id`, and `document_id`.
