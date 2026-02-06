from pydantic import BaseModel, Field
from typing import List, Optional

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_added: int


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    document_ids: Optional[List[str]] = None


class SourceChunk(BaseModel):
    document_id: Optional[str]
    document_name: Optional[str]
    chunk_index: Optional[int]
    page_number: Optional[int]
    text: str
    confidence: float


class AskResponse(BaseModel):
    answer: str
    session_id: str
    sources: List[SourceChunk]


class ChatMessageResponse(BaseModel):
    role: str
    content: str
    created_at: str


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageResponse]
