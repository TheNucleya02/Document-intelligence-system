import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()
    COLLECTION_NAME = "pdf_docs"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    CHROMA_DB_DIR = os.path.join(os.getcwd(), "chroma_db")
    UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")

    # Ensure Mistral key is set in env for LangChain
    os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY

settings = Settings()