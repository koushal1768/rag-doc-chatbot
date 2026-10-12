import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    doc_id: uuid.UUID = Field(..., description="Target document ID to query against.")
    thread_id: Optional[uuid.UUID] = Field(
        default=None, 
        description="Optional thread ID. If omitted, uses active thread or creates a new one."
    )
    message: str = Field(..., example="What is the key takeaway from Section 3?")


class CitationSnippet(BaseModel):
    page: int
    snippet: str


class ChatQueryResponse(BaseModel):
    thread_id: uuid.UUID
    answer: str
    citations: List[CitationSnippet]