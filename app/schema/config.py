import uuid
from typing import Optional
from pydantic import BaseModel, Field


class ClientConfigBase(BaseModel):
    provider: str = Field(default="openai", description="Options: 'openai', 'gemini', 'claude'")
    model_name: str = Field(default="gpt-4o-mini", description="e.g., 'gpt-4o-mini', 'gemini-1.5-flash', 'claude-3-5-sonnet'")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    system_prompt: str = Field(
        default="You are an expert AI assistant answering questions strictly based on the provided PDF documents."
    )
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None


class ClientConfigUpdate(ClientConfigBase):
    pass


class ClientConfigOut(ClientConfigBase):
    id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True