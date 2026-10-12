import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.document import Document
from app.services.storage_service import delete_pdf_file


def create_document_record(
    db: Session, user_id: str, doc_id: uuid.UUID, filename: str, file_path: str, file_size: int
) -> Document:
    doc = Document(
        id=doc_id,
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        status="PENDING"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_user_documents(db: Session, user_id: str) -> List[Document]:
    return db.query(Document).filter(Document.user_id == user_id).all()


def get_document_by_id(db: Session, user_id: str, doc_id: uuid.UUID) -> Optional[Document]:
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return doc


def delete_document(db: Session, user_id: str, doc_id: uuid.UUID) -> None:
    doc = get_document_by_id(db, user_id, doc_id)
    
    # 1. Delete physical file
    delete_pdf_file(doc.file_path)
    
    # 2. Delete database record
    db.delete(doc)
    db.commit()