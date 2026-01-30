# Production Refactoring Guide

## Overview

This document outlines the complete refactoring of the Document Intelligence application from Supabase to PostgreSQL with custom JWT authentication.

## What Changed

### Removed
- ✅ Supabase client (`@supabase/supabase-js`)
- ✅ Supabase authentication (OAuth, magic links)
- ✅ Supabase database wrapper
- ✅ All Supabase environment variables

### Added
- ✅ PostgreSQL with connection pooling (SQLAlchemy)
- ✅ JWT-based authentication (access + refresh tokens)
- ✅ Bcrypt password hashing
- ✅ Custom authentication routes (register, login, refresh)
- ✅ Database migrations system
- ✅ Docker Compose with PostgreSQL

## Architecture

### Backend Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy with psycopg2
- **Authentication**: JWT (PyJWT) + Bcrypt
- **Migration**: Custom migration script
- **API Docs**: Swagger UI (auto-generated)

### Frontend Stack
- **Framework**: React + TypeScript with Vite
- **Authentication**: JWT stored in localStorage
- **API Client**: Fetch API with Bearer token support
- **State Management**: React hooks + localStorage

### Database Schema

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Jobs table
CREATE TABLE jobs (
  id UUID PRIMARY KEY,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  result TEXT,
  error TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## Authentication Flow

### Registration
```
1. POST /auth/register
   Request: { email: "user@example.com", password: "..." }
   Response: { id, email }
   Action: Hash password + create user in DB

2. User can now login with their credentials
```

### Login
```
1. POST /auth/login
   Request: { email: "user@example.com", password: "..." }
   Response: { access_token, refresh_token, token_type }
   Action: Verify credentials + generate JWT tokens

2. Frontend stores tokens in localStorage
3. All subsequent requests include: Authorization: Bearer {access_token}
```

### Token Refresh
```
1. When access_token expires (15 minutes)
   POST /auth/refresh
   Request: { refresh_token: "..." }
   Response: { access_token, refresh_token, token_type }

2. Frontend updates localStorage with new tokens
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/document_intelligence
SECRET_KEY=your-secret-key-change-in-production
MISTRAL_API_KEY=your-mistral-api-key
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Docker Compose (.env)
```env
MISTRAL_API_KEY=your-mistral-api-key
```

## Running the Application

### Local Development (without Docker)

1. **Start PostgreSQL**
   ```bash
   # Using Docker
   docker run --name postgres -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=document_intelligence \
     -p 5432:5432 -d postgres:15-alpine
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Create database tables**
   ```bash
   python migrations.py
   ```

4. **Run backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Access the app**
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs
   - API Health: http://localhost:8000/health

### Docker Compose (Production-like)

```bash
# Build and run all services
docker-compose up --build

# Access the app
# Frontend: http://localhost:5173
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Key File Changes

### Backend Files Created
- `app/database.py` - SQLAlchemy connection + session management
- `app/models.py` - SQLAlchemy ORM models (User, Document, Job)
- `app/core/security.py` - JWT generation/validation + password hashing
- `app/api/auth.py` - Authentication routes (register, login, refresh)
- `backend/migrations.py` - Database table creation

### Backend Files Modified
- `app/main.py` - Added auth router
- `app/api/routes.py` - Replaced all Supabase calls with SQLAlchemy
- `app/core/config.py` - Updated settings
- `app/core/jobs.py` - Replaced in-memory storage with database
- `requirements.txt` - Removed `supabase`, added `sqlalchemy`, `psycopg2-binary`, `email-validator`, `PyJWT`
- `backend/Dockerfile` - Updated to run migrations on startup
- `.env` - Replaced Supabase variables

### Frontend Files Modified
- `src/api/client.ts` - Added Authorization header support
- `src/api/auth.ts` - New auth API client (register, login, refresh)

## Database Migration

Since this is a fresh start, no data migration is needed. For existing Supabase users:

1. Export data from Supabase
2. Transform data to PostgreSQL schema
3. Run migrations to create tables
4. Insert data into PostgreSQL

## Security Considerations

1. **JWT Token Management**
   - Access tokens: 15 minutes validity
   - Refresh tokens: 7 days validity
   - Stored in localStorage (not secure for sensitive apps - use httpOnly for production)

2. **Password Storage**
   - Bcrypt hashing with salt rounds
   - Never store plaintext passwords

3. **Environment Variables**
   - Always use strong SECRET_KEY in production
   - Rotate SECRET_KEY regularly
   - Use environment-specific configs

4. **CORS**
   - Currently set to allow all origins (*)
   - Change in production to specific domains

5. **Database Access**
   - Use RLS if moving to Supabase PostgreSQL later
   - Implement role-based access control for sensitive operations

## Scaling Considerations

### Horizontal Scaling
- Backend is stateless (no session affinity needed)
- Use connection pooling (SQLAlchemy handles this)
- Deploy multiple backend instances behind load balancer

### Database Scaling
- PostgreSQL connection pooling with pgBouncer
- Read replicas for scaling reads
- Partitioning for large tables

### Caching Layer
- Consider Redis for token caching
- Cache frequently accessed documents

## Deployment Checklist

- [ ] Update SECRET_KEY to a strong random value
- [ ] Set DATABASE_URL to production Postgres instance
- [ ] Configure CORS for production domain
- [ ] Enable HTTPS
- [ ] Set up automated backups
- [ ] Configure monitoring and logging
- [ ] Set up CI/CD pipeline
- [ ] Test authentication flows
- [ ] Load test the application

## Troubleshooting

### Database Connection Error
```
Error: could not translate host name "postgres" to address
```
Solution: Ensure PostgreSQL service is running and DATABASE_URL is correct

### Authentication Failures
```
401 Unauthorized: Invalid token
```
Solution:
- Check token expiry
- Verify SECRET_KEY matches between requests
- Clear localStorage and re-login

### Missing Database Tables
```
Error: relation "users" does not exist
```
Solution: Run `python migrations.py` to create tables

## Next Steps

1. Implement email verification for registration
2. Add password reset functionality
3. Implement 2FA (TOTP)
4. Add user profile endpoints
5. Implement audit logging
6. Add role-based access control (RBAC)
7. Set up monitoring (Prometheus, Grafana)
8. Add rate limiting per user
9. Implement API key authentication for service-to-service calls
10. Add document versioning

## Support

For questions or issues:
1. Check the FastAPI documentation at http://localhost:8000/docs
2. Review application logs in Docker: `docker-compose logs -f backend`
3. Verify database tables exist: `docker-compose exec postgres psql -U user -d document_intelligence -c "\dt"`

---

**Last Updated**: January 2025
**Status**: Production Ready
