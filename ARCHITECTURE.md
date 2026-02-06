# Document Intelligence System - Architecture

## System Overview
A minimal, backend-first RAG application for learning and production-style patterns. The UI is simple HTML + Bootstrap and serves only as an API client.

## Tech Stack
- FastAPI + SQLAlchemy
- PostgreSQL (Docker) or SQLite (local)
- Chroma DB for embeddings
- Mistral AI for LLM + embeddings

## Core Pipeline
```
Upload → Parse → Clean Text → Chunk → Embed → Store → Retrieve → Answer
```

## API Layer
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /documents/upload`
- `GET /documents/list`
- `POST /chat/ask`
- `GET /chat/history`
- `GET /health`

## Data Layer
Tables:
- `users`
- `documents`
- `document_chunks`
- `chat_sessions`
- `chat_messages`

`document_chunks` stores deterministic chunk metadata:
- `document_id`, `user_id`, `page_number`, `chunk_index`, `text`

`chat_sessions` binds the session to a document set.
`chat_messages` stores the full chat history and sources.

## LLM Layer
Single abstraction in `app/services/llm.py` with explicit prompt structure:
- Instruction
- Retrieved chunks
- Chat history
- User question

Rules are enforced in the system prompt:
- Never hallucinate
- Say “I don’t know” if answer is not in chunks
- Always cite document name + chunk index

## Observability
Structured logging includes:
- `request_id`
- `user_id`
- `document_id`

## Minimal UI
Static HTML is served at:
- `/login`
- `/register`
- `/upload`
- `/chat`

No SPA framework or build tools are used.
