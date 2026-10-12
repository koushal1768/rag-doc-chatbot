import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schema.document import DocumentOut, DocumentUploadResponse
from app.services.storage_service import save_pdf_file
from app.services.document_service import (
    create_document_record,
    get_user_documents,
    get_document_by_id,
    delete_document
)
from app.workers.ingestion_worker import process_pdf_ingestion  # <-- Import Worker

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Uploads a PDF file, saves it to isolated tenant storage, and queues async vector indexing."""
    doc_id = uuid.uuid4()
    
    # Save file physically
    file_path, file_size = save_pdf_file(file, str(current_user.id), doc_id)
    
    # Create DB record in PENDING state
    doc = create_document_record(
        db=db,
        user_id=str(current_user.id),
        doc_id=doc_id,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size
    )

    # Queue background task for PDF ingestion
    background_tasks.add_task(
        process_pdf_ingestion,
        doc_id=doc.id,
        user_id=current_user.id,
        file_path=file_path
    )

    return {
        "message": "PDF uploaded successfully. Processing started in background.",
        "doc_id": doc.id,
        "filename": doc.filename,
        "status": doc.status
    }


@router.get("", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all uploaded documents belonging to the authenticated user."""
    return get_user_documents(db, str(current_user.id))


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document_status(
    doc_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Checks processing status and details for a specific document."""
    return get_document_by_id(db, str(current_user.id), doc_id)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    doc_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes a document from disk and database."""
    delete_document(db, str(current_user.id), doc_id)
    return None