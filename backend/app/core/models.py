from pydantic import BaseModel
from typing import List

class QuestionRequest(BaseModel):
    question: str
    session_id: str = "default"

class DocumentUploadResponse(BaseModel):
    message: str
    chunks_count: int
    files_count: int

class QuestionResponse(BaseModel):
    answer: str
    sources: List[str] = []