import os
import time
from uuid import uuid4
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.models import QuestionRequest, QuestionResponse, DocumentUploadResponse
from app.services.ingestion.loader import ensure_upload_dir
from app.services.vector_store import process_and_store_files, get_vector_store, clear_vector_store
from app.services.chat import get_conversational_chain
from app.services.chat import chat_histories

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "PDF Q&A API is running"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@router.get("/documents")
async def list_documents():
    """List all unique filenames in the vector store."""
    vector_store = get_vector_store()
    # Note: This is an expensive operation in Chroma if not optimized.
    # A lighter approach is maintaining a separate SQL table for file tracking.
    # For now, we fetch metadata:
    data = vector_store._collection.get(include=["metadatas"])
    unique_files = set(meta['file_name'] for meta in data['metadatas'] if 'file_name' in meta)
    return {"files": list(unique_files)}

@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a specific file from the index."""
    vector_store = get_vector_store()
    try:
        # Delete items where metadata 'file_name' matches
        vector_store._collection.delete(where={"file_name": filename})
        return {"message": f"Document '{filename}' deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    try:
        upload_dir = ensure_upload_dir()
        saved_paths = []
        original_filenames = []

        for file in files:
            filename = f"{uuid4()}_{file.filename}"
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as f_out:
                f_out.write(await file.read())
            saved_paths.append(file_path)
            original_filenames.append(file.filename)

        chunks_added = process_and_store_files(saved_paths, original_filenames)

        return DocumentUploadResponse(
            message="Files processed and stored.",
            chunks_count=chunks_added,
            files_count=len(files),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process documents: {str(e)}")

@router.post("/chat", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    try:
        # Check if DB exists
        try:
            vector_store = get_vector_store()
            if vector_store._collection.count() == 0:
                 raise HTTPException(status_code=404, detail="No documents found. Please upload first.")
        except Exception:
             raise HTTPException(status_code=404, detail="No documents found. Please upload first.")

        chain = get_conversational_chain()
        
        response = chain.invoke(
            {"input": request.question},
            config={"configurable": {"session_id": request.session_id}},
        )

        sources = []
        if "context" in response:
            for doc in response["context"]:
                if hasattr(doc, 'metadata') and 'file_name' in doc.metadata:
                    sources.append(doc.metadata['file_name'])
        
        sources = list(dict.fromkeys(sources))
        return QuestionResponse(answer=response["answer"], sources=sources)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@router.get("/collections")
async def list_collections():
    try:
        vector_store = get_vector_store()
        doc_count = vector_store._collection.count()
        return {"collections": [{"name": vector_store._collection.name, "document_count": doc_count}]}
    except Exception as e:
        return {"collections": [], "error": str(e)}

@router.delete("/clear-documents")
async def clear_documents_endpoint():
    try:
        if clear_vector_store():
             return {"message": "All documents cleared successfully"}
        return {"message": "No documents to clear"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")
    

@router.delete("/chat/{session_id}")
async def reset_chat_history(session_id: str):
    if session_id in chat_histories:
        del chat_histories[session_id]
        return {"message": f"History cleared for session {session_id}"}
    raise HTTPException(status_code=404, detail="Session ID not found")