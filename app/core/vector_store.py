import os
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

VECTOR_DB_DIR = "./vector_db_data"
os.makedirs(VECTOR_DB_DIR, exist_ok=True)


def get_embedding_function():
    """Initializes standard OpenAI Embeddings or a fallback embedding model."""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        # Fallback to standard environment variable if not in Settings
        api_key = os.getenv("OPENAI_API_KEY", "placeholder_key")
    
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key
    )


class VectorStoreService:
    def __init__(self):
        self.chroma_dir = VECTOR_DB_DIR

    def get_vector_store(self) -> Chroma:
        """Returns persistent ChromaDB vector store instance."""
        embedding_fn = get_embedding_function()
        return Chroma(
            persist_directory=self.chroma_dir,
            embedding_function=embedding_fn,
            collection_name="rag_pdf_documents"
        )

    def add_documents(self, documents: List[Any]) -> None:
        """Indexes chunked documents into ChromaDB."""
        vector_store = self.get_vector_store()
        vector_store.add_documents(documents)

    def similarity_search(
        self, query: str, user_id: str, doc_id: str, top_k: int = 4
    ) -> List[Any]:
        """Performs similarity search enforced with user_id and doc_id metadata filters."""
        vector_store = self.get_vector_store()
        
        # Hard multi-tenant metadata filter
        metadata_filter = {
            "$and": [
                {"user_id": str(user_id)},
                {"doc_id": str(doc_id)}
            ]
        }
        
        return vector_store.similarity_search(
            query=query,
            k=top_k,
            filter=metadata_filter
        )


vector_store_service = VectorStoreService()