from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Core
    SECRET_KEY: str
    DATABASE_URL: str

    # LLM Mistral
    MISTRAL_API_KEY: Optional[str] = None
    LLM_MODEL: str = "mistral-large-latest"
    EMBEDDING_MODEL: str = "mistral-embed"

    # LLM Gemini
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_LLM_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBED_MODEL: str = "models/text-embedding-004"

    # LangSmith
    LANGSMITH_TRACING: Optional[str] = None
    LANGSMITH_ENDPOINT: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = None

    # RAG Tuning
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_K: int = 4

    # Pinecone Vector Store
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX_NAME: str = "doc-intel"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
