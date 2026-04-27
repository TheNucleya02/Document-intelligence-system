import json
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..db.models import Conversation
from ..models.schemas import QueryRequest, QueryResponse, Source, ConversationResponse, UploadResponse
from ..services.rag import process_pdf, query_rag, stream_query_rag
from ..services.vector_store import clear_vector_store

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Uploads a PDF, chunks it, and stores it in the vector database."""
    chunks_created = await process_pdf(file)
    return UploadResponse(
        message="Document processed and stored successfully.",
        filename=file.filename,
        chunks=chunks_created
    )

@router.post("/query")
async def query_document(request: QueryRequest, db: Session = Depends(get_db)):
    """Queries the document system. Supports optional streaming and document filtering."""
    if request.stream:
        # For streaming, we yield chunks. Note: Saving to DB during streaming is trickier.
        # We'll stream the response and not save to DB for simplicity in this streaming endpoint,
        # or we could collect it. To keep it robust, we won't log streaming to DB in this basic version,
        # or we log just the question.
        generator = stream_query_rag(request.query, request.filter_doc)
        return StreamingResponse(generator, media_type="text/event-stream")
    
    # Non-streaming
    answer, docs = await query_rag(request.query, request.filter_doc)
    
    sources = [Source(content=d.page_content, metadata=d.metadata) for d in docs]
    
    # Save to SQLite
    sources_json = json.dumps([d.metadata for d in docs])
    db_conv = Conversation(
        question=request.query,
        answer=answer,
        sources=sources_json
    )
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)
    
    return QueryResponse(answer=answer, sources=sources)

@router.get("/history", response_model=list[ConversationResponse])
def get_history(db: Session = Depends(get_db), limit: int = 50):
    """Retrieves conversation history."""
    conversations = db.query(Conversation).order_by(Conversation.created_at.desc()).limit(limit).all()
    return conversations

@router.delete("/history")
def clear_history(db: Session = Depends(get_db)):
    """Clears all conversation history."""
    db.query(Conversation).delete()
    db.commit()
    return {"message": "History cleared."}

@router.delete("/documents")
def clear_documents():
    """Clears the vector database."""
    clear_vector_store()
    return {"message": "Vector database cleared."}
