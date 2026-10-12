import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("threads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    sender = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)  # Page numbers and source snippets
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))