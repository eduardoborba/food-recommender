"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.recipes import router as recipes_router

app = FastAPI(title="Food Recommender API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://localhost:19006"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(recipes_router)


@app.get("/health")
def health():
    return {"status": "ok", "database": settings.database_url.split("@")[-1]}
