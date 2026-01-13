import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document
from app.core.config import settings

# OCR
from app.services.ocr.processor import ocr_pdf, ocr_image_file

# Jobs
from app.core.jobs import JobStatus, update_job_status


def ensure_upload_dir() -> str:
    path = Path(settings.UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


# -----------------------------
# Background Task Entry Point
# -----------------------------

def process_upload_background_task(
    job_id: str,
    file_paths: List[str],
    document_id: str,
):
    """
    This function runs in the background.
    Pipeline:
    File -> OCR/Text -> Chunking -> Embedding -> Chroma
    All chunks are tagged with document_id.
    """
    try:
        print(f"[{job_id}] Starting background processing for {len(file_paths)} files...")
        update_job_status(job_id, JobStatus.PROCESSING)

        # Import here to avoid circular import
        from app.services.vector_store import process_and_store_files

        # IMPORTANT: pass document_id
        chunks_added = process_and_store_files(
            file_paths=file_paths,
            document_id=document_id,
        )

        result = {
            "message": "Files processed and stored successfully",
            "chunks_added": chunks_added,
            "files_processed": len(file_paths),
            "document_id": document_id,
        }

        update_job_status(job_id, JobStatus.COMPLETED, result=result)
        print(f"[{job_id}] Processing complete.")

    except Exception as e:
        print(f"[{job_id}] Processing failed: {e}")
        update_job_status(job_id, JobStatus.FAILED, error=str(e))

    finally:
        # Clean up temp files
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)


# -----------------------------
# Document Loading (OCR aware)
# -----------------------------

def load_docs_from_path(path: str, document_id: str) -> List[Document]:
    """
    Loads a file, applies OCR if needed, and ALWAYS attaches document_id in metadata.
    """
    suffix = Path(path).suffix.lower()

    if suffix == ".pdf":
        # 1. Try standard text extraction first
        try:
            loader = PyPDFLoader(path)
            docs = loader.load()

            total_content_length = sum(len(doc.page_content.strip()) for doc in docs)

            if total_content_length > 50:
                # Attach document_id to all pages
                for d in docs:
                    d.metadata["document_id"] = document_id
                    d.metadata["source"] = path
                    d.metadata["is_ocr"] = False
                return docs

            print(f"Standard extraction returned empty/low text for {path}. Attempting OCR...")

        except Exception as e:
            print(f"Standard loading error for {path}: {e}. Attempting OCR...")

        # 2. OCR fallback
        extracted_text = ocr_pdf(path)
        if extracted_text.strip():
            return [
                Document(
                    page_content=extracted_text,
                    metadata={
                        "source": path,
                        "document_id": document_id,
                        "is_ocr": True,
                    },
                )
            ]
        return []

    elif suffix in [".jpg", ".jpeg", ".png"]:
        text = ocr_image_file(path)
        print(f"OCR text length for {path}: {len(text)}")
        if text.strip():
            return [
                Document(
                    page_content=text,
                    metadata={
                        "source": path,
                        "document_id": document_id,
                        "is_ocr": True,
                    },
                )
            ]
        return []

    elif suffix == ".docx":
        docs = Docx2txtLoader(path).load()
        for d in docs:
            d.metadata["document_id"] = document_id
            d.metadata["source"] = path
            d.metadata["is_ocr"] = False
        return docs

    return []
