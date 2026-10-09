from fastapi import FastAPI
from app.api.v1.endpoints import auth
from app.api.v1.routers import api_router
from app.core.database import Base, engine

# Auto-create tables for development (Use Alembic for production migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG Multi-Tenant Platform")

@app.get("/heath")
def heath():
    return {"app is running smothely"}


app.include_router(api_router, prefix="/api/v1")