"""Pydantic schemas for API request/response."""

from pydantic import BaseModel


class RecipeSummary(BaseModel):
    id: int
    name: str
    minutes: int | None
    tags: list[str] | None
    image_url: str | None

    model_config = {"from_attributes": True}


class RecipeDetail(RecipeSummary):
    description: str | None
    steps: list[str] | None
    nutrition: dict | None


class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[RecipeSummary]
