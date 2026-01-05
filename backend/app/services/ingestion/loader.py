import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document
from app.core.config import settings

# Import our new OCR processor
from app.services.ocr.processor import ocr_pdf, ocr_image_file

def ensure_upload_dir() -> str:
    path = Path(settings.UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)

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