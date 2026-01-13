import os
from uuid import uuid4
from typing import List

from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from app.core.config import settings
from app.services.ingestion.loader import load_docs_from_path
from app.services.chunking.splitter import intelligent_chunk_documents


# -----------------------------
# Vector Store Factory
# -----------------------------

def get_vector_store():
    """
    Returns the Chroma vector store instance.
    """
    embeddings_model = MistralAIEmbeddings(model="mistral-embed")
    persist_dir = settings.CHROMA_DB_DIR

    os.makedirs(persist_dir, exist_ok=True)

    return Chroma(
        collection_name=settings.COLLECTION_NAME,
        embedding_function=embeddings_model,
        persist_directory=persist_dir,
    )


# -----------------------------
# Ingestion Entry Point
# -----------------------------

def process_and_store_files(
    file_paths: List[str],
    document_id: str,
) -> int:
    """
    Loads files, applies OCR if needed, chunks, embeds, and stores in Chroma.
    Every chunk is tagged with document_id.
    """
    all_docs: List[Document] = []

    # 1. Load documents (OCR aware)
    for path in file_paths:
        print(f"Loading documents from: {path}")

        docs = load_docs_from_path(path, document_id=document_id)

        print(f"Loaded {len(docs)} docs from {path}")

        all_docs.extend(docs)

    if not all_docs:
        print("No documents loaded. Nothing to store.")
        return 0

    print(f"Total loaded docs: {len(all_docs)}")

    # 2. Chunk
    chunked_docs = intelligent_chunk_documents(all_docs)
    print(f"Total chunks created: {len(chunked_docs)}")

    if not chunked_docs:
        print("No chunks created. Nothing to store.")
        return 0

    # 3. Store in Chroma
    vectordb = get_vector_store()

    # Ensure each chunk still has document_id (safety check)
    for doc in chunked_docs:
        if "document_id" not in doc.metadata:
            doc.metadata["document_id"] = document_id

    ids = [str(uuid4()) for _ in range(len(chunked_docs))]

    print(f"Adding {len(chunked_docs)} chunks to vector store...")

    vectordb.add_documents(documents=chunked_docs, ids=ids)
    vectordb.persist()

    return len(chunked_docs)
