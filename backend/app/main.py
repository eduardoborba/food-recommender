"""FastAPI application entry point."""

from fastapi import FastAPI

from app.config import settings
from app.routers.recipes import router as recipes_router

app = FastAPI(title="Food Recommender API", version="0.1.0")
app.include_router(recipes_router)


@app.get("/health")
def health():
    return {"status": "ok", "database": settings.database_url.split("@")[-1]}
