import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document
from app.core.config import settings

# Import our new OCR processor
from app.services.ocr.processor import ocr_pdf, ocr_image_file
from app.core.jobs import JobStatus, update_job_status
# Removed: from app.services.vector_store import process_and_store_files  # Circular import

def ensure_upload_dir() -> str:
    path = Path(settings.UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)

# --- Background Task Function ---
def process_upload_background_task(job_id: str, file_paths: List[str]):
    """
    This function runs in the background. It performs the heavy lifting:
    OCR -> Chunking -> Embedding -> ChromaDB
    """
    try:
        print(f"[{job_id}] Starting background processing for {len(file_paths)} files...")
        update_job_status(job_id, JobStatus.PROCESSING)
        
        # Import here to avoid circular import
        from app.services.vector_store import process_and_store_files
        
        # This is the heavy function from your vector_store.py
        chunks_added = process_and_store_files(file_paths)
        
        result = {
            "message": "Files processed and stored successfully",
            "chunks_added": chunks_added,
            "files_processed": len(file_paths)
        }
        
        update_job_status(job_id, JobStatus.COMPLETED, result=result)
        print(f"[{job_id}] Processing complete.")
        
    except Exception as e:
        print(f"[{job_id}] Processing failed: {e}")
        update_job_status(job_id, JobStatus.FAILED, error=str(e))
    finally:
        # Optional: Clean up temp files if you don't want to keep them on disk forever
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)


def load_docs_from_path(path: str) -> List[Document]:
    suffix = Path(path).suffix.lower()
    
    if suffix == ".pdf":
        # 1. Try standard text extraction first (Fast)
        try:
            loader = PyPDFLoader(path)
            docs = loader.load()
            
            # Check if the extracted text is meaningful.
            # Scanned PDFs often return empty strings or just whitespace.
            total_content_length = sum(len(doc.page_content.strip()) for doc in docs)
            
            if total_content_length > 50:  # Threshold: assume valid text exists
                return docs
                
            print(f"Standard extraction returned empty/low text for {path}. Attempting OCR...")
            
        except Exception as e:
            print(f"Standard loading error for {path}: {e}. Attempting OCR...")

        # 2. Fallback to OCR (Slow but effective)
        extracted_text = ocr_pdf(path)
        if extracted_text.strip():
            # Return as a single Document (metadata marks it as OCR)
            return [Document(page_content=extracted_text, metadata={"source": path, "is_ocr": True})]
        return []

    # New: Support for direct image uploads
    elif suffix in [".jpg", ".jpeg", ".png"]:
        text = ocr_image_file(path)
        print(f"OCR text length for {path}: {len(text)}")
        if text.strip():
            return [Document(page_content=text, metadata={"source": path, "is_ocr": True})]
        return []

    elif suffix == ".docx":
        return Docx2txtLoader(path).load()
        
    return []