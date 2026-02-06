import os
import logging
from uuid import uuid4
from typing import List

from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from app.core.config import settings
from app.services.ingestion.loader import load_docs_from_path
from app.services.chunking.splitter import intelligent_chunk_documents
from app.db.session import SessionLocal
from app.db.models import DocumentChunk

logger = logging.getLogger(__name__)


# -----------------------------
# Vector Store Factory
# -----------------------------

def get_vector_store():
    """
    Returns the Chroma vector store instance.
    """
    embeddings_model = MistralAIEmbeddings(model=settings.EMBEDDING_MODEL)
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
    user_id: str,
    document_name: str,
) -> int:
    """
    Loads files, applies OCR if needed, chunks, embeds, and stores in Chroma.
    Every chunk is tagged with document_id.
    """
    all_docs: List[Document] = []

    # 1. Load documents (OCR aware)
    for path in file_paths:
        logger.info("Loading documents", extra={"path": path})

        docs = load_docs_from_path(
            path,
            document_id=document_id,
            user_id=user_id,
            document_name=document_name,
        )

        logger.info("Loaded docs", extra={"count": len(docs), "path": path})

        all_docs.extend(docs)

    if not all_docs:
        logger.warning("No documents loaded. Nothing to store.")
        return 0

    logger.info("Total loaded docs", extra={"count": len(all_docs)})

    # 2. Chunk
    chunked_docs = intelligent_chunk_documents(all_docs)
    logger.info("Total chunks created", extra={"count": len(chunked_docs)})

    if not chunked_docs:
        logger.warning("No chunks created. Nothing to store.")
        return 0

    # 3. Store in Chroma
    vectordb = get_vector_store()

    # Ensure each chunk still has document_id (safety check)
    for index, doc in enumerate(chunked_docs):
        if "document_id" not in doc.metadata:
            doc.metadata["document_id"] = document_id
        doc.metadata["user_id"] = user_id
        doc.metadata["document_name"] = document_name
        doc.metadata["chunk_index"] = index
        doc.metadata.setdefault("page_number", None)

    ids = [str(uuid4()) for _ in range(len(chunked_docs))]

    logger.info("Adding chunks to vector store", extra={"count": len(chunked_docs)})

    vectordb.add_documents(documents=chunked_docs, ids=ids)
    vectordb.persist()

    db = SessionLocal()
    try:
        for doc, chunk_id in zip(chunked_docs, ids):
            db_chunk = DocumentChunk(
                id=chunk_id,
                document_id=document_id,
                user_id=user_id,
                chunk_index=doc.metadata.get("chunk_index", 0),
                page_number=doc.metadata.get("page_number"),
                text=doc.page_content,
            )
            db.add(db_chunk)
        db.commit()
    finally:
        db.close()

    return len(chunked_docs)
