import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.thread import Thread
from app.models.chat_message import ChatMessage
from app.schema.thread import ThreadCreate
from app.services.memory_service import memory_service


def create_new_thread(db: Session, user_id: uuid.UUID, thread_in: ThreadCreate) -> Thread:
    """Deactivates all previous active threads for this user and initializes a new thread."""
    # Deactivate existing active threads for this user
    db.query(Thread).filter(
        Thread.user_id == user_id,
        Thread.is_active == True
    ).update({"is_active": False})

    # Create new active thread
    new_thread = Thread(
        user_id=user_id,
        doc_id=thread_in.doc_id,
        title=thread_in.title,
        is_active=True
    )
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)
    return new_thread


def get_active_thread(db: Session, user_id: uuid.UUID, doc_id: Optional[uuid.UUID] = None) -> Optional[Thread]:
    """Fetches the user's currently active chat thread."""
    query = db.query(Thread).filter(Thread.user_id == user_id, Thread.is_active == True)
    if doc_id:
        query = query.filter(Thread.doc_id == doc_id)
    return query.first()


def list_user_threads(db: Session, user_id: uuid.UUID) -> List[Thread]:
    """Lists all historical chat threads for a user."""
    return db.query(Thread).filter(Thread.user_id == user_id).order_by(Thread.updated_at.desc()).all()


def get_thread_by_id(db: Session, user_id: uuid.UUID, thread_id: uuid.UUID) -> Thread:
    """Gets a specific thread and verifies user ownership."""
    thread = db.query(Thread).filter(Thread.id == thread_id, Thread.user_id == user_id).first()
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found.")
    return thread


def add_message_to_thread(
    db: Session, thread_id: uuid.UUID, sender: str, content: str, citations: Optional[List[dict]] = None
) -> ChatMessage:
    """Saves message to Postgres long-term storage and pushes to Redis short-term cache."""
    msg = ChatMessage(
        thread_id=thread_id,
        sender=sender,
        content=content,
        citations=citations
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # Push to Redis buffer
    memory_service.push_message(str(thread_id), sender, content)
    return msg


def delete_thread_cascade(db: Session, user_id: uuid.UUID, thread_id: uuid.UUID) -> None:
    """Deletes thread, messages from Postgres, and memory buffer from Redis."""
    thread = get_thread_by_id(db, user_id, thread_id)
    memory_service.clear_thread_memory(str(thread_id))
    db.delete(thread)
    db.commit()