import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.vector_store import vector_store_service
from app.services.config_service import get_user_config
from app.services.llm_factory.factory import LLMFactory
from app.services.memory_service import memory_service
from app.services.thread_service import (
    get_thread_by_id,
    get_active_thread,
    create_new_thread,
    add_message_to_thread
)
from app.schema.thread import ThreadCreate


class RAGService:
    def execute_rag_query(
        self,
        db: Session,
        user_id: uuid.UUID,
        doc_id: uuid.UUID,
        message: str,
        thread_id: uuid.UUID | None = None
    ) -> Dict[str, Any]:
        
        # 1. Resolve or initialize Thread
        if thread_id:
            thread = get_thread_by_id(db, user_id, thread_id)
        else:
            thread = get_active_thread(db, user_id, doc_id)
            if not thread:
                thread = create_new_thread(
                    db, user_id, ThreadCreate(doc_id=doc_id, title=message[:30] + "...")
                )

        # 2. Retrieve top-k relevant chunks from Vector DB with metadata filter
        retrieved_docs = vector_store_service.similarity_search(
            query=message,
            user_id=str(user_id),
            doc_id=str(doc_id),
            top_k=4
        )

        if not retrieved_docs:
            context_str = "No relevant context found in the target document."
            citations = []
        else:
            context_str = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
            citations = [
                {
                    "page": doc.metadata.get("page", 1),
                    "snippet": doc.page_content[:150] + "..."
                }
                for doc in retrieved_docs
            ]

        # 3. Retrieve User LLM Config & instantiate dynamic adapter
        user_config = get_user_config(db, str(user_id))
        llm_adapter = LLMFactory.get_adapter(user_config)

        # 4. Load recent short-term conversation history from Redis
        history = memory_service.get_recent_messages(str(thread.id), limit=6)
        formatted_history = "\n".join(
            [f"{msg['sender'].capitalize()}: {msg['content']}" for msg in history]
        )

        # 5. Build full system prompt with history & context
        full_system_prompt = (
            f"{user_config.system_prompt}\n\n"
            f"Prior Conversation History:\n{formatted_history or 'None'}"
        )

        # 6. Generate answer from selected LLM model
        answer = llm_adapter.generate_response(
            prompt=message,
            system_prompt=full_system_prompt,
            temperature=user_config.temperature,
            context=context_str
        )

        # 7. Persist User Question & Assistant Answer into DB and Redis Cache
        add_message_to_thread(
            db=db,
            thread_id=thread.id,
            sender="user",
            content=message
        )
        add_message_to_thread(
            db=db,
            thread_id=thread.id,
            sender="assistant",
            content=answer,
            citations=citations
        )

        return {
            "thread_id": thread.id,
            "answer": answer,
            "citations": citations
        }


rag_service = RAGService()