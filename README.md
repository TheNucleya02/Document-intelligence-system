# 📚 Document Intelligence System

A production-ready document question-answering system that allows users to upload PDF and DOCX files and ask questions about their content using advanced AI technology. Built with FastAPI backend, React frontend, and PostgreSQL database.

## ✨ Features

### 🚀 **Core Functionality**
- **Multi-format Document Support**: Upload PDF and DOCX files
- **Intelligent Text Chunking**: Smart document segmentation for optimal retrieval
- **Conversational AI**: Ask follow-up questions with context awareness
- **Source Attribution**: Get references to specific documents that informed the answer
- **Session Management**: Maintain conversation history across interactions

### 🔐 **Security & Authentication**
- **JWT Authentication**: Secure token-based authentication
- **User Registration & Login**: Email + password based authentication
- **Bcrypt Password Hashing**: Industry-standard password security
- **Token Refresh Mechanism**: Automatic token rotation
- **Document Ownership**: Users can only access their documents

### 🎯 **Production Ready**
- **PostgreSQL Database**: Scalable relational database
- **Docker Compose**: Easy deployment and development setup
- **Connection Pooling**: Optimized database connections
- **Error Handling**: Comprehensive error management
- **Health Monitoring**: API status and diagnostics
- **RESTful API**: Well-documented with Swagger UI

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose OR Python 3.10+, Node.js 18+
- Mistral AI API key

### With Docker Compose (Recommended)

```bash
git clone <repo-url> && cd document-intelligence
echo "MISTRAL_API_KEY=your-key-here" > .env
docker-compose up --build
```

**Access:**
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Without Docker

**Backend:**
```bash
cd backend && pip install -r requirements.txt
python migrations.py
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend && npm install && npm run dev
```

## 🔐 Authentication

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure123"}'

# Use token in requests
curl -H "Authorization: Bearer <token>" http://localhost:8000/documents
```

## 📋 API Endpoints

**Auth:** `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`

**Documents:** `GET/POST /documents`, `DELETE /documents/{id}`, `POST /documents/{id}/analyze`

**Chat:** `POST /chat`, `GET /jobs/{id}`, `GET /health`

## 🏗️ Architecture

```
Frontend (React)   ←HTTP/JWT→   Backend (FastAPI)   ←→   PostgreSQL
                                      ↓
                            Chroma DB + Mistral AI
```

## 🐳 Services

- **PostgreSQL**: User & document storage
- **FastAPI**: REST API with Swagger at `/docs`
- **React**: Frontend with TypeScript & Tailwind

## 🔒 Security

- JWT (15min access, 7day refresh tokens)
- Bcrypt password hashing
- CORS & rate limiting
- Document ownership enforcement

## 📁 Key Files

```
backend/
├── app/database.py          # SQLAlchemy setup
├── app/models.py            # ORM models
├── app/core/security.py     # JWT & auth
├── app/api/auth.py          # Auth routes
└── migrations.py            # DB setup

frontend/
├── src/api/auth.ts          # Auth client
├── src/api/client.ts        # API wrapper
└── src/pages/               # React pages
```

## 🚀 Deployment

**Environment Variables:**
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-secret-key-here
MISTRAL_API_KEY=your-api-key
VITE_API_BASE_URL=https://api.yourdomain.com
```

## 🛠️ Commands

```bash
docker-compose logs -f backend           # Logs
docker-compose exec postgres psql ...    # Database CLI
docker-compose down -v                   # Reset all
npm run build                            # Build frontend
```

## 📖 Documentation

See [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md) for detailed architecture documentation.

## 🐛 Troubleshooting

**DB Connection Error**: Check `docker-compose ps`
**401 Unauthorized**: Re-login, check token in DevTools
**Port in Use**: Change port in `docker-compose.yml`

## 📄 License

MIT License

---

**Production-ready. Scalable. Secure. Built with FastAPI, React, and PostgreSQL.**
