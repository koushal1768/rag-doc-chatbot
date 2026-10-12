from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schema.chat import ChatQueryRequest, ChatQueryResponse
from app.services.rag_service import rag_service

router = APIRouter()


@router.post("", response_model=ChatQueryResponse, status_code=status.HTTP_200_OK)
def chat_with_pdf(
    request: ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Executes a multi-tenant RAG query against a user's uploaded PDF document."""
    result = rag_service.execute_rag_query(
        db=db,
        user_id=current_user.id,
        doc_id=request.doc_id,
        message=request.message,
        thread_id=request.thread_id
    )
    return result