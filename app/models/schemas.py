from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class QueryRequest(BaseModel):
    query: str
    filter_doc: Optional[str] = None
    stream: bool = False

class Source(BaseModel):
    content: str
    metadata: dict

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]

class ConversationResponse(BaseModel):
    id: int
    question: str
    answer: str
    sources: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks: int
