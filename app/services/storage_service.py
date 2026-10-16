import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException, status

BASE_STORAGE_DIR = "storage"


def ensure_user_storage_dir(user_id: str) -> str:
    """Creates a user-isolated folder if it does not exist."""
    user_dir = os.path.join(BASE_STORAGE_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def save_pdf_file(file: UploadFile, user_id: str, doc_id: uuid.UUID) -> tuple[str, int]:
    """Validates and saves uploaded PDF to isolated directory."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are supported."
        )

    user_dir = ensure_user_storage_dir(user_id)
    file_path = os.path.join(user_dir, f"{doc_id}.pdf")

    # Read and save file content
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        return file_path, file_size
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save PDF file: {str(e)}"
        )


def delete_pdf_file(file_path: str) -> None:
    """Removes file from local storage."""
    if os.path.exists(file_path):
        os.remove(file_path)