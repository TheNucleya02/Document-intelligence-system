# Document Intelligence System - Architecture Documentation

## System Overview

The Document Intelligence System is a production-ready RAG (Retrieval-Augmented Generation) application that enables users to upload documents and ask questions about their content using AI.

### Tech Stack

**Backend:**
- Framework: FastAPI 0.95+
- Database: PostgreSQL 15
- ORM: SQLAlchemy 2.0+
- Authentication: JWT (PyJWT)
- Password Hashing: Bcrypt
- Vector Store: Chroma DB (local)
- LLM: Mistral AI

**Frontend:**
- Framework: React 18 + TypeScript
- Build Tool: Vite
- Styling: Tailwind CSS
- HTTP Client: Fetch API

**Infrastructure:**
- Containerization: Docker & Docker Compose
- Database: PostgreSQL with connection pooling
- Application Server: Uvicorn ASGI

## Application Layers

### 1. Presentation Layer (Frontend)

**Location:** `frontend/src/`

Components:
- React pages for authentication, documents, chat
- Vite development server (port 5173)
- TypeScript for type safety
- Tailwind CSS for styling

Authentication:
- JWT tokens stored in localStorage
- Bearer token included in all API requests
- Automatic token refresh on expiry

### 2. API Layer (Backend)

**Location:** `backend/app/api/`

Routers:
- **auth.py**: Authentication endpoints
  - `POST /auth/register` - User registration
  - `POST /auth/login` - User login
  - `POST /auth/refresh` - Token refresh

- **routes.py**: Document & chat endpoints
  - `GET /documents` - List user documents
  - `POST /documents` - Upload documents
  - `DELETE /documents/{id}` - Delete document
  - `POST /documents/{id}/analyze` - Analyze document
  - `POST /chat` - Ask question about documents
  - `GET /jobs/{id}` - Check upload job status
  - `GET /health` - Health check

### 3. Security Layer

**Location:** `backend/app/core/security.py`

Components:
- **Password Management**
  - `hash_password()` - Bcrypt hashing
  - `verify_password()` - Bcrypt verification

- **JWT Management**
  - `create_tokens()` - Generate access + refresh tokens
  - `create_access_token()` - Access token (15 min)
  - `create_refresh_token()` - Refresh token (7 days)
  - `decode_token()` - Validate and decode JWT
  - `get_current_user()` - Dependency for protected routes

### 4. Data Layer (Database)

**Location:** `backend/app/database.py`, `backend/app/models.py`

Components:
- **SQLAlchemy Engine**
  - PostgreSQL connection with pooling
  - Connection pool: size=10, max_overflow=20

- **ORM Models**
  ```
  User
  ├── id (UUID)
  ├── email (VARCHAR, UNIQUE)
  ├── password_hash (VARCHAR)
  └── documents (relationship)

  Document
  ├── id (UUID)
  ├── filename (VARCHAR)
  ├── owner_id (FK to User)
  ├── status (ENUM)
  └── created_at, updated_at (TIMESTAMP)

  Job
  ├── id (UUID)
  ├── status (VARCHAR)
  ├── result (JSON)
  └── error (TEXT)
  ```

### 5. Business Logic Layer

**Location:** `backend/app/services/`

Services:
- **Vector Store**: Chroma DB for embeddings
- **Chat**: LangChain conversational chain
- **Ingestion**: Document loading and chunking
- **OCR**: Text extraction from images/PDFs
- **Extraction**: Document structure analysis
- **Chunking**: Intelligent text splitting

### 6. Job Processing Layer

**Location:** `backend/app/core/jobs.py`

Features:
- Background task processing
- Job status tracking in database
- Result/error storage
- Async document processing

## Data Flow

### Authentication Flow

```
1. User Registration
   User Input (email, password)
      ↓
   POST /auth/register
      ↓
   Backend: Hash password with bcrypt
      ↓
   Create User in PostgreSQL
      ↓
   Return user data

2. User Login
   User Input (email, password)
      ↓
   POST /auth/login
      ↓
   Backend: Verify credentials
      ↓
   Generate JWT tokens
      ↓
   Return { access_token, refresh_token }
      ↓
   Frontend: Store in localStorage

3. Protected Request
   Frontend: Add "Authorization: Bearer {token}"
      ↓
   Backend: Validate token
      ↓
   Extract user_id from token
      ↓
   Load User from database
      ↓
   Execute business logic
```

### Document Processing Flow

```
1. Upload
   File Input
      ↓
   POST /documents (with Bearer token)
      ↓
   Backend: Save file to disk
      ↓
   Create Document record in DB
      ↓
   Create Job record in DB
      ↓
   Queue background task
      ↓
   Return immediately with job_id

2. Background Processing
   Load document from disk
      ↓
   Extract text (OCR if needed)
      ↓
   Split into chunks
      ↓
   Generate embeddings (Mistral AI)
      ↓
   Store in Chroma DB
      ↓
   Update Job status to COMPLETED

3. Query
   User question + token
      ↓
   POST /chat (with Bearer token)
      ↓
   Backend: Get user's document IDs
      ↓
   Query Chroma with semantic search
      ↓
   Generate response with LLM
      ↓
   Return answer + sources
```

## Security Model

### Authentication

- **Token-Based**: JWT prevents session state on server
- **Stateless**: Scalable across multiple backend instances
- **Token Rotation**: Refresh tokens enable secure expiry
- **Time-Limited**: Access tokens expire in 15 minutes

### Authorization

- **Document Ownership**: Users filtered by owner_id
- **Query Isolation**: Chat queries filter by user's documents
- **Dependency Injection**: `get_current_user()` on protected routes

### Password Security

- **Bcrypt Hashing**: Industry standard with salt
- **No Plaintext**: Never stored or logged
- **Configurable Salt**: Default 10 rounds

## Deployment Architecture

### Development (Local)

```
Docker Compose
├── PostgreSQL (port 5432)
├── FastAPI (port 8000)
│   └── Uvicorn ASGI server
└── React Dev (port 5173)
    └── Vite dev server
```

### Production (Recommended)

```
Load Balancer (HTTPS)
    ↓
[Backend Pod 1] ─┐
[Backend Pod 2] ─┼─ Database (PostgreSQL)
[Backend Pod 3] ─┘   ├── Replicas
                     └── Backups

CDN (Static Assets)
    ↓
[Frontend] (Vite build)
```

## Performance Considerations

### Database
- **Connection Pooling**: 10 connections, 20 overflow
- **Indexes**: Automatic on primary keys and foreign keys
- **Query Optimization**: SQLAlchemy lazy loading

### API
- **Rate Limiting**: Slowapi middleware
  - Document upload: 5/minute
  - Chat: 20/minute
  - Job polling: 60/minute

### Caching
- **Vector Store**: Local Chroma (disk-based)
- **Token Cache**: Consider Redis for distributed systems

## Scalability Roadmap

### Phase 1 (Current)
- Single backend instance
- PostgreSQL on managed service
- Local Chroma DB

### Phase 2 (Next)
- Multiple backend instances behind load balancer
- Redis for distributed token caching
- S3/MinIO for file storage

### Phase 3 (Future)
- Distributed Chroma DB
- Message queue (Redis/RabbitMQ)
- Worker processes for async tasks
- Metrics and monitoring (Prometheus/Grafana)

## Error Handling

### HTTP Status Codes
- 200 OK: Successful request
- 201 Created: Resource created
- 204 No Content: Successful with no response body
- 400 Bad Request: Invalid input
- 401 Unauthorized: Missing/invalid token
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Resource not found
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Server error

### Error Response Format
```json
{
  "detail": "Error description"
}
```

## Configuration Management

### Environment-Based
- Development: `DATABASE_URL=postgresql://localhost:5432/dev`
- Production: `DATABASE_URL=postgresql://prod-server:5432/prod`

### Configuration Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `MISTRAL_API_KEY`: LLM API key
- `VITE_API_BASE_URL`: Frontend API endpoint

## Monitoring & Logging

### Health Checks
- `GET /health` - API status
- Docker Compose health checks for PostgreSQL

### Logging
- FastAPI logs via Uvicorn
- Database query logs (configurable)
- Application error logs

### Future Enhancements
- Structured logging (JSON format)
- Log aggregation (ELK/Loki)
- Distributed tracing
- APM (Application Performance Monitoring)

## Testing Strategy

### Unit Tests
- Password hashing functions
- Token generation/validation
- Permission checks

### Integration Tests
- Auth flow (register → login → token refresh)
- Document lifecycle (upload → query → delete)
- Error scenarios

### End-to-End Tests
- User workflows through frontend
- API documentation accuracy

## Database Migrations

### Creating New Schema
1. Define models in `app/models.py`
2. Run `python migrations.py`
3. SQLAlchemy auto-creates tables

### Updating Schema
For production, use Alembic (future enhancement):
```bash
alembic revision --autogenerate -m "Add new column"
alembic upgrade head
```

## Disaster Recovery

### Backup Strategy
- Daily automated PostgreSQL backups
- Point-in-time recovery enabled
- Test restore procedures monthly

### High Availability
- Database replication
- Read replicas for scaling
- Connection pooling for resilience

## Compliance & Security

### Data Protection
- HTTPS/TLS in transit
- Passwords hashed at rest
- Environment secrets not in code

### Access Control
- JWT-based authentication
- Row-level authorization
- Audit logs (future)

---

**Version**: 1.0
**Last Updated**: January 2025
**Status**: Production Ready
