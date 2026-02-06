import os
import shutil
import time
from uuid import uuid4
import logging
from fastapi import Request
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models import User, Document, DocumentStatus, ChatMessage, ChatSession
from app.core.logging import set_document_id, reset_document_id
from app.services.ingestion.loader import ensure_upload_dir
from app.services.vector_store import process_and_store_files
from app.services.chat import answer_question
from app.core.limiter import limiter
from app.core.models import (
    DocumentUploadResponse,
    AskRequest,
    AskResponse,
    ChatHistoryResponse,
    ChatMessageResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# --------------------
# Health
# --------------------

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}


# --------------------
# Documents
# --------------------

@router.get("/documents/list")
async def list_documents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all documents belonging to the current user.
    """
    documents = db.query(Document).filter(
        Document.owner_id == user.id
    ).order_by(Document.created_at.desc()).all()

    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "status": doc.status,
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat(),
        }
        for doc in documents
    ]


@router.post("/documents/upload", response_model=DocumentUploadResponse)
@limiter.limit("5/minute")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    upload_dir = ensure_upload_dir()
    stored_filename = f"{uuid4()}_{file.filename}"
    file_path = os.path.join(upload_dir, stored_filename)

    with open(file_path, "wb") as f_out:
        shutil.copyfileobj(file.file, f_out)

    document_id = str(uuid4())
    token = set_document_id(document_id)
    document = Document(
        id=document_id,
        filename=file.filename,
        owner_id=user.id,
        status=DocumentStatus.PROCESSING,
    )

    db.add(document)
    db.commit()

    try:
        chunks_added = process_and_store_files(
            file_paths=[file_path],
            document_id=document_id,
            user_id=user.id,
            document_name=file.filename,
        )
        document.status = DocumentStatus.COMPLETED
        db.commit()
    except Exception as exc:
        logger.exception("Document processing failed")
        document.status = DocumentStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        reset_document_id(token)
        if os.path.exists(file_path):
            os.remove(file_path)

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        chunks_added=chunks_added,
    )


# --------------------
# Chat
# --------------------

@router.post("/chat/ask", response_model=AskResponse)
@limiter.limit("20/minute")
async def ask_question(
    request: Request,
    req: AskRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = answer_question(
            db=db,
            user_id=user.id,
            question=req.question,
            session_id=req.session_id,
            document_ids=req.document_ids,
        )
    except ValueError as exc:
        detail = str(exc)
        status = 400
        if detail == "Chat session not found":
            status = 404
        raise HTTPException(status_code=status, detail=detail) from exc

    return AskResponse(**result)

@router.get("/chat/history", response_model=ChatHistoryResponse)
@limiter.limit("60/minute")
async def chat_history(
    request: Request,
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    response_messages = [
        ChatMessageResponse(
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]
    return ChatHistoryResponse(session_id=session_id, messages=response_messages)
