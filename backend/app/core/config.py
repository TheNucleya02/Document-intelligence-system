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
    COLLECTION_NAME = "pdf_docs"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    CHROMA_DB_DIR = os.path.join(os.getcwd(), "chroma_db")
    UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")

    os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY

settings = Settings()