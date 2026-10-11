from fastapi import APIRouter
from app.api.v1.endpoints import auth, config, documents, threads, chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(config.router, prefix="/config", tags=["Client Config"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(threads.router, prefix="/threads", tags=["Threads"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat & RAG"])