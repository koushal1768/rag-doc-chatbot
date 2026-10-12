import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    filename: str
    file_size: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    message: str
    doc_id: uuid.UUID
    filename: str
    status: str