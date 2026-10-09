from fastapi import APIRouter
from app.api.v1.endpoints import auth, config

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(config.router, prefix="/config", tags=["Client Config"])