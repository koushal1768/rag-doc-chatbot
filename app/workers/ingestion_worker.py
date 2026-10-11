import uuid
import logging
from sqlalchemy.orm import Session
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.database import SessionLocal
from app.models.document import Document
from app.core.vector_store import vector_store_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_pdf_ingestion(doc_id: uuid.UUID, user_id: uuid.UUID, file_path: str):
    """Background task function to load, split, embed, and index PDF documents."""
    db: Session = SessionLocal()
    
    try:
        logger.info(f"Starting ingestion for doc_id={doc_id}, user_id={user_id}")
        
        # 1. Update Document status to PROCESSING
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            logger.error(f"Document record {doc_id} not found.")
            return
        
        doc.status = "PROCESSING"
        db.commit()

        # 2. Extract text page-by-page from PDF
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        if not pages:
            raise ValueError("PDF file is empty or could not be read.")

        # 3. Chunk text recursively
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(pages)

        # 4. Attach multi-tenant metadata to each chunk
        for chunk in chunks:
            chunk.metadata["user_id"] = str(user_id)
            chunk.metadata["doc_id"] = str(doc_id)
            chunk.metadata["page"] = chunk.metadata.get("page", 0) + 1

        # 5. Index chunks into Vector DB
        vector_store_service.add_documents(chunks)

        # 6. Mark Document as INDEXED
        doc.status = "INDEXED"
        doc.error_message = None
        db.commit()
        logger.info(f"Successfully indexed doc_id={doc_id} ({len(chunks)} chunks created).")

    except Exception as e:
        logger.error(f"Error ingesting doc_id={doc_id}: {str(e)}")
        db.rollback()
        # Update Document status to FAILED with error detail
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = "FAILED"
            doc.error_message = str(e)
            db.commit()

    finally:
        db.close()