# 📄 DocIntel: Production-Grade RAG Document Intelligence System

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain)](https://python.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**DocIntel** is a high-performance, scalable Document Intelligence System built with a focus on modern AI engineering practices. It leverages **Retrieval-Augmented Generation (RAG)** to turn static PDF documents into interactive, searchable, and conversational knowledge bases.

---

## 🚀 Key Features

-   **🧠 Intelligent RAG Pipeline**: Optimized retrieval using LangChain and Pinecone/ChromaDB for highly relevant context extraction.
-   **⚡ Streaming Responses**: Real-time answer generation using Server-Sent Events (SSE) for a snappy, ChatGPT-like user experience.
-   **📂 Advanced PDF Processing**: Robust ingestion with `PyPDF` and `RecursiveCharacterTextSplitter` to maintain logical document structure and context.
-   **🤖 Multi-LLM Support**: Seamlessly switch between **Mistral AI** (primary) and **Google Gemini** (fallback) based on availability and cost.
-   **📜 Conversation History**: Persistent storage of queries and AI responses using **PostgreSQL/SQLAlchemy** for long-term user context.
-   **🔍 Observability**: Full execution tracing integrated with **LangSmith** for debugging, latency monitoring, and prompt optimization.
-   **🐳 Cloud Native**: Fully containerized with Docker, optimized for stateless deployment on platforms like Render or Railway.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.11) |
| **Orchestration** | LangChain |
| **LLMs** | Mistral Large, Gemini 1.5 Flash |
| **Vector Database** | Pinecone / ChromaDB |
| **Relational Database** | PostgreSQL (via SQLAlchemy) |
| **Deployment** | Docker, Docker Compose |
| **Observability** | LangSmith |

---

## 🏗️ Architecture Overview

The system follows a modular, service-oriented architecture designed for separation of concerns:

1.  **API Layer (`app/routes`)**: RESTful endpoints for document upload, conversational querying, and history management.
2.  **Service Layer (`app/services`)**: Business logic for PDF processing, vector store interactions, and RAG chain execution.
3.  **Data Layer (`app/db`, `app/models`)**: Managed schemas and database sessions for persistence.
4.  **Configuration (`app/utils`)**: Pydantic-based environment management for secure and typed settings.

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- API Keys for Mistral AI (or Gemini) and Pinecone

### Local Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/TheNucleya02/DocIntel.git
    cd DocIntel
    ```

2.  **Configure Environment Variables**:
    Create a `.env` file in the root directory:
    ```bash
    cp .env.example .env
    # Add your API keys to .env
    ```

3.  **Run with Docker Compose**:
    ```bash
    docker compose up --build
    ```
    The API will be available at `http://localhost:8000`.

4.  **Interactive Documentation**:
    Explore the API via Swagger UI at `http://localhost:8000/docs`.

---

## 📊 Environment Variables

| Variable | Description |
| :--- | :--- |
| `DATABASE_URL` | PostgreSQL or SQLite connection string |
| `MISTRAL_API_KEY` | Your Mistral AI API key |
| `GOOGLE_API_KEY` | Google Gemini API key (fallback) |
| `PINECONE_API_KEY` | Pinecone vector store key |
| `LANGSMITH_API_KEY` | For observability and tracing |

---

## 🛤️ Roadmap

- [ ] **Multi-modal Support**: Ingest and query images/tables within PDFs.
- [ ] **Custom Embeddings**: Finetune embedding models for specific domain knowledge.
- [ ] **Frontend UI**: A sleek Next.js dashboard for document management.
- [ ] **Hybrid Search**: Combine semantic search with keyword (BM25) search for better accuracy.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@TheNucleya02](https://github.com/TheNucleya02)
- LinkedIn: [Your Profile](https://linkedin.com/in/amanjha02)

---

> [!TIP]
> This project was built with a "Production-First" mindset, implementing proper error handling, logging, and database sanitization for real-world reliability.
