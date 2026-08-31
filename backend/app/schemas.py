"""Pydantic schemas for API request/response."""

from pydantic import BaseModel, field_validator


class RecipeSummary(BaseModel):
    id: int
    name: str
    minutes: int | None
    tags: list[str] | None
    image_url: str | None

    @field_validator("image_url", mode="after")
    @classmethod
    def empty_image_is_none(cls, v: str | None) -> str | None:
        """Enrichment marks checked-but-imageless recipes with ''."""
        return v or None

    model_config = {"from_attributes": True}


class RecipeDetail(RecipeSummary):
    description: str | None
    steps: list[str] | None
    nutrition: dict | None


class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[RecipeSummary]
