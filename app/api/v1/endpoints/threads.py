import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schema.thread import ThreadCreate, ThreadOut, ChatMessageOut
from app.services.thread_service import (
    create_new_thread,
    get_active_thread,
    list_user_threads,
    get_thread_by_id,
    delete_thread_cascade
)

router = APIRouter()


@router.post("", response_model=ThreadOut, status_code=status.HTTP_201_CREATED)
def create_thread(
    thread_in: ThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initializes a new thread, setting it as active and deactivating prior threads."""
    return create_new_thread(db, current_user.id, thread_in)


@router.get("", response_model=List[ThreadOut])
def get_all_threads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all historical threads created by the user."""
    return list_user_threads(db, current_user.id)


@router.get("/active", response_model=ThreadOut)
def get_current_active_thread(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches the user's currently active thread."""
    active_thread = get_active_thread(db, current_user.id)
    if not active_thread:
        raise HTTPException(status_code=404, detail="No active thread found. Please create a new thread.")
    return active_thread


@router.get("/{thread_id}/messages", response_model=List[ChatMessageOut])
def get_thread_messages(
    thread_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches the full persistent message history for a specific thread."""
    thread = get_thread_by_id(db, current_user.id, thread_id)
    return thread.messages


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_thread(
    thread_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes a thread and all associated messages from DB and cache."""
    delete_thread_cascade(db, current_user.id, thread_id)
    return None