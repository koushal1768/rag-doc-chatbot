import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ThreadCreate(BaseModel):
    doc_id: uuid.UUID
    title: Optional[str] = "New Conversation"


class ThreadOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    doc_id: uuid.UUID
    title: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageOut(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    sender: str
    content: str
    citations: Optional[List[dict]] = None
    created_at: datetime

    class Config:
        from_attributes = True