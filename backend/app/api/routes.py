import os
import shutil
import time
from uuid import uuid4
from typing import List
from fastapi import Request
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models import User, Document, Job, DocumentStatus

from app.services.ingestion.loader import ensure_upload_dir, process_upload_background_task
from app.services.vector_store import get_vector_store
from app.services.chat import get_conversational_chain
from app.services.extraction.extractor import analyze_document_structure
from app.core.limiter import limiter
from app.core.models import QuestionRequest, QuestionResponse

router = APIRouter()


# --------------------
# Health
# --------------------

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}


# --------------------
# Documents
# --------------------

@router.get("/documents")
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


@router.post("/documents")
@limiter.limit("5/minute")
async def upload_documents(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None,
    request: Request = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload documents, create one job per document, return immediately.
    """
    upload_dir = ensure_upload_dir()
    responses = []

    for file in files:
        stored_filename = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(upload_dir, stored_filename)

        with open(file_path, "wb") as f_out:
            shutil.copyfileobj(file.file, f_out)

        document_id = str(uuid4())
        document = Document(
            id=document_id,
            filename=file.filename,
            owner_id=user.id,
            status=DocumentStatus.PENDING,
        )

        db.add(document)
        db.commit()

        job_id = str(uuid4())
        job = Job(id=job_id)
        db.add(job)
        db.commit()

        background_tasks.add_task(
            process_upload_background_task,
            job_id=job_id,
            file_paths=[file_path],
            document_id=document_id,
        )

        responses.append({
            "document_id": document_id,
            "job_id": job_id,
            "filename": file.filename,
        })

    return {
        "message": "Upload accepted. Processing started.",
        "items": responses,
    }


@router.delete("/documents/{document_id}")
async def delete_document(
    request: Request,
    document_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a document:
    - Verify ownership
    - Delete from vector store
    - Delete from database
    """
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == user.id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    vector_store = get_vector_store()
    vector_store._collection.delete(where={"document_id": document_id})

    db.delete(doc)
    db.commit()

    return {"message": "Document deleted successfully"}


# --------------------
# Jobs
# --------------------

@router.get("/jobs/{job_id}")
@limiter.limit("60/minute")
async def get_job_status(
    request: Request,
    job_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Poll job status.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "status": job.status,
        "result": job.result,
        "error": job.error,
        "created_at": job.created_at.isoformat(),
    }


# --------------------
# Chat
# --------------------

@router.post("/chat", response_model=QuestionResponse)
@limiter.limit("20/minute")
async def ask_question(
    request: Request,
    req: QuestionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ask question over ONLY the current user's documents.
    """
    docs = db.query(Document).filter(Document.owner_id == user.id).all()
    document_ids = [d.id for d in docs]

    if not document_ids:
        raise HTTPException(status_code=404, detail="No documents found")

    chain = get_conversational_chain(
        filter={"document_id": {"$in": document_ids}}
    )

    response = chain.invoke(
        {"input": req.question},
        config={"configurable": {"session_id": req.session_id}},
    )

    sources = []
    if "context" in response:
        for doc in response["context"]:
            if hasattr(doc, "metadata") and "document_id" in doc.metadata:
                sources.append(doc.metadata["document_id"])

    sources = list(dict.fromkeys(sources))

    return QuestionResponse(answer=response["answer"], sources=sources)


# --------------------
# Analysis
# --------------------

@router.post("/documents/{document_id}/analyze")
@limiter.limit("5/minute")
async def analyze_document(
    request: Request,
    document_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze ONE document belonging to the user.
    """
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == user.id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    analysis = analyze_document_structure(document_id=document_id)

    return analysis
