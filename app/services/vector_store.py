import os
import shutil
from langchain_chroma import Chroma
from langchain_mistralai import MistralAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.utils.config import settings

def get_embeddings():
    if settings.MISTRAL_API_KEY:
        return MistralAIEmbeddings(
            mistral_api_key=settings.MISTRAL_API_KEY,
            model=settings.EMBEDDING_MODEL
        )
    elif settings.GOOGLE_API_KEY:
        return GoogleGenerativeAIEmbeddings(
            google_api_key=settings.GOOGLE_API_KEY,
            model=settings.GEMINI_EMBED_MODEL
        )
    else:
        raise ValueError("No embedding model API key configured (Mistral or Google).")

def get_vector_store():
    embeddings = get_embeddings()
    # Create the data directory if it doesn't exist
    persist_directory = "./data/chroma"
    os.makedirs(persist_directory, exist_ok=True)
    
    return Chroma(
        collection_name="doc_intel",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

def clear_vector_store():
    persist_directory = "./data/chroma"
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
    # Recreate the directory
    os.makedirs(persist_directory, exist_ok=True)
