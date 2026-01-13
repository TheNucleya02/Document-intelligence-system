import os
import shutil
import time
from uuid import uuid4
from typing import List
from fastapi import Request
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks

from app.core.auth import get_current_user
from app.core.supabase import supabase
from app.core.jobs import create_job, get_job

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
async def list_documents(user_id: str = Depends(get_current_user)):
    """
    List all documents belonging to the current user (from SQL, not Chroma).
    """
    result = (
        supabase.table("documents")
        .select("*")
        .eq("owner_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return result.data


@router.post("/documents")
@limiter.limit("5/minute")
async def upload_documents(
    request: Request,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user),
):
    """
    Upload documents, create one job per document, return immediately.
    """
    upload_dir = ensure_upload_dir()

    responses = []

    for file in files:
        # 1. Save file
        stored_filename = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(upload_dir, stored_filename)

        with open(file_path, "wb") as f_out:
            shutil.copyfileobj(file.file, f_out)

        # 2. Create document row
        document_id = str(uuid4())

        supabase.table("documents").insert({
            "id": document_id,
            "filename": file.filename,
            "status": "processing",
            "owner_id": user_id,
        }).execute()

        # 3. Create job
        job_id = str(uuid4())
        create_job(job_id)

        # 4. Start background ingestion
        background_tasks.add_task(
            process_upload_background_task,
            job_id=job_id,
            file_paths=[file_path],
            document_id=document_id,   # 👈 IMPORTANT: pass document_id
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
    user_id: str = Depends(get_current_user),
):
    """
    Delete a document:
    - Verify ownership
    - Delete from vector store
    - Delete from SQL
    """
    # 1. Check ownership
    doc = (
        supabase.table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("owner_id", user_id)
        .single()
        .execute()
    )

    if not doc.data:
        raise HTTPException(status_code=404, detail="Document not found")

    # 2. Delete from vector store
    vector_store = get_vector_store()
    vector_store._collection.delete(where={"document_id": document_id})

    # 3. Delete from SQL
    supabase.table("documents").delete().eq("id", document_id).execute()

    return {"message": "Document deleted successfully"}


# --------------------
# Jobs
# --------------------

@router.get("/jobs/{job_id}")
@limiter.limit("60/minute")
async def get_job_status(
    request: Request,
    job_id: str,
    user_id: str = Depends(get_current_user),
):
    """
    Poll job status.
    (Later you should also store job ownership in DB.)
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


# --------------------
# Chat
# --------------------

@router.post("/chat", response_model=QuestionResponse)
@limiter.limit("20/minute")
async def ask_question(
    request: Request,
    req: QuestionRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Ask question over ONLY the current user's documents.
    """
    # 1. Get user's document IDs
    docs = (
        supabase.table("documents")
        .select("id")
        .eq("owner_id", user_id)
        .execute()
    )

    document_ids = [d["id"] for d in docs.data]

    if not document_ids:
        raise HTTPException(status_code=404, detail="No documents found")

    # 2. Run retrieval filtered by document_id
    chain = get_conversational_chain(
        filter={"document_id": {"$in": document_ids}}
    )

    response = chain.invoke(
        {"input": request.question},
        config={"configurable": {"session_id": request.session_id}},
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
    user_id: str = Depends(get_current_user),
):
    """
    Analyze ONE document belonging to the user.
    """
    # 1. Check ownership
    doc = (
        supabase.table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("owner_id", user_id)
        .single()
        .execute()
    )

    if not doc.data:
        raise HTTPException(status_code=404, detail="Document not found")

    # 2. Run analysis (you should later pass document_id into this)
    analysis = analyze_document_structure(document_id=document_id)

    return analysis
