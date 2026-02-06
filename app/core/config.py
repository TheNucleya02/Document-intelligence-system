import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/document_intelligence"
    )
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    LLM_MODEL = os.getenv("LLM_MODEL", "mistral-large-latest")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "mistral-embed")
    COLLECTION_NAME = "pdf_docs"
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "4"))
    CHROMA_DB_DIR = os.path.join(os.getcwd(), "data", "vector_store")
    UPLOAD_DIR = os.path.join(os.getcwd(), "data", "uploads")

    os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY

settings = Settings()
