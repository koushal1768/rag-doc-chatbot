from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routers import api_router
from app.core.database import Base, engine

# Auto-create tables for development (Use Alembic for production migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG Multi-Tenant Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/heath")
def heath():
    return {"app is running smothly"}


app.include_router(api_router, prefix="/api/v1")