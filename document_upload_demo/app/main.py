from fastapi import FastAPI
from app.api.v1.routes_ingestion import router as ingestion_router

app = FastAPI(
    title="Document Ingestion API",
    version="1.0.0"
)

app.include_router(ingestion_router, prefix="/admin/documents", tags=["Ingestion"])
