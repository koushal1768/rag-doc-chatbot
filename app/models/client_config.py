import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ClientConfig(Base):
    __tablename__ = "client_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # LLM Settings
    provider = Column(String, default="openai", nullable=False)  # "openai", "gemini", "claude"
    model_name = Column(String, default="gpt-4o-mini", nullable=False)
    temperature = Column(Float, default=0.2, nullable=False)
    system_prompt = Column(
        Text, 
        default="You are an expert AI assistant answering questions strictly based on the provided PDF documents.",
        nullable=False
    )
    
    # Optional User-provided API Keys (BYOK)
    openai_api_key = Column(String, nullable=True)
    gemini_api_key = Column(String, nullable=True)
    claude_api_key = Column(String, nullable=True)

    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="config")