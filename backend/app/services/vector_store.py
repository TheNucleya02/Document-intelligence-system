import os
from pathlib import Path
from uuid import uuid4
from typing import List

from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from app.core.config import settings
from app.services.ingestion.loader import load_docs_from_path
from app.services.chunking.splitter import intelligent_chunk_documents

def get_vector_store():
    """Returns the Chroma vector store instance."""
    embeddings_model = MistralAIEmbeddings(model="mistral-embed")
    persist_dir = settings.CHROMA_DB_DIR
    
    return Chroma(
        collection_name=settings.COLLECTION_NAME,
        embedding_function=embeddings_model,
        persist_directory=persist_dir,
    )

def process_and_store_files(file_paths: List[str], original_filenames: List[str] = None) -> int:
    all_docs = []
    
    # 1. Load
    for i, path in enumerate(file_paths):
        print(f"Loading documents from: {path}")
        docs = load_docs_from_path(path)
        print(f"Loaded {len(docs)} documents from {path}")
        original_name = original_filenames[i] if original_filenames and i < len(original_filenames) else Path(path).name
        for doc in docs:
            doc.metadata = {
                **(doc.metadata or {}),
                "source": doc.metadata.get("source", str(path)),
                "file_name": original_name,
            }
        all_docs.extend(docs)

    print(f"Total documents loaded: {len(all_docs)}")
    if not all_docs:
        print("No documents to process")
        return 0

    # 2. Chunk
    chunked = intelligent_chunk_documents(all_docs)
    print(f"Total chunks created: {len(chunked)}")

    if not chunked:
        print("No chunks to store")
        return 0

    # 3. Store
    persist_dir = settings.CHROMA_DB_DIR
    os.makedirs(persist_dir, exist_ok=True)
    
    embeddings_model = MistralAIEmbeddings(model="mistral-embed")
    vectordb = Chroma(
        collection_name=settings.COLLECTION_NAME,
        embedding_function=embeddings_model,
        persist_directory=persist_dir,
    )
    
    ids = [str(uuid4()) for _ in range(len(chunked))]
    print(f"Adding {len(chunked)} chunks to vector store")
    vectordb.add_documents(documents=chunked, ids=ids)
    vectordb.persist()
    
    return len(chunked)

def clear_vector_store():
    persist_dir = settings.CHROMA_DB_DIR
    if os.path.isdir(persist_dir):
        import shutil
        shutil.rmtree(persist_dir)
        return True
    return False