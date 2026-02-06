from typing import List, Dict, Any
import logging
from app.services.vector_store import get_vector_store
from app.core.config import settings

logger = logging.getLogger(__name__)


def retrieve_chunks(
    question: str,
    document_ids: List[str],
    user_id: str,
) -> List[Dict[str, Any]]:
    if not document_ids:
        return []
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_score(
        question,
        k=settings.RETRIEVAL_K,
        filter={"document_id": {"$in": document_ids}, "user_id": user_id},
    )

    chunks: List[Dict[str, Any]] = []
    for doc, distance in results:
        metadata = doc.metadata or {}
        confidence = 1 / (1 + float(distance)) if distance is not None else 0.0
        chunks.append(
            {
                "document_id": metadata.get("document_id"),
                "document_name": metadata.get("document_name"),
                "chunk_index": metadata.get("chunk_index"),
                "page_number": metadata.get("page_number"),
                "text": doc.page_content,
                "confidence": round(confidence, 4),
            }
        )

    logger.info("Retrieved chunks", extra={"count": len(chunks)})
    return chunks
