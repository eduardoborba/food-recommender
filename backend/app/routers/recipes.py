"""Recipe search and detail endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Recipe
from app.schemas import RecipeDetail, RecipeSummary, SearchResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/recipes/search", response_model=SearchResponse)
def search_recipes(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search recipes by name or tags."""
    like_pattern = f"%{q}%"
    results = (
        db.query(Recipe)
        .filter(or_(Recipe.name.ilike(like_pattern), Recipe.tags.any(q.lower())))
        .order_by(Recipe.name)
        .limit(limit)
        .offset(offset)
        .all()
    )

    return SearchResponse(
        query=q,
        count=len(results),
        results=[RecipeSummary.model_validate(r) for r in results],
    )


@router.get("/recipes/{recipe_id}", response_model=RecipeDetail)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get full recipe details including steps and nutrition."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RecipeDetail.model_validate(recipe)


@router.get("/recipes")
def list_recipes(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tag: str | None = Query(None, description="Filter by tag"),
    db: Session = Depends(get_db),
):
    """List recipes, optionally filtered by tag."""
    q = db.query(Recipe)
    if tag:
        q = q.filter(Recipe.tags.any(tag.lower()))
    recipes = q.order_by(Recipe.name).limit(limit).offset(offset).all()
    return [RecipeSummary.model_validate(r) for r in recipes]


@router.get("/tags")
def list_tags(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    """List the most common recipe tags."""
    rows = (
        db.query(func.unnest(Recipe.tags).label("tag"), func.count().label("count"))
        .group_by("tag")
        .order_by(text("count DESC"))
        .limit(limit)
        .all()
    )
    return [{"tag": r.tag, "count": r.count} for r in rows]


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    """Database statistics."""
    return {
        "recipes": db.query(func.count(Recipe.id)).scalar(),
        "recipes_with_image": db.query(func.count(Recipe.id)).filter(Recipe.image_url.isnot(None)).scalar(),
    }
