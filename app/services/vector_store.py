import os
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
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
    if not settings.PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY is missing. Please set it in your environment or .env file.")
    
    return PineconeVectorStore(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=embeddings,
        pinecone_api_key=settings.PINECONE_API_KEY
    )

def clear_vector_store():
    if not settings.PINECONE_API_KEY:
        return
        
    try:
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        index.delete(delete_all=True)
    except Exception as e:
        print(f"Error clearing Pinecone index: {e}")
