"""SQLAlchemy models for Phase 1."""

from sqlalchemy import Column, Date, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from app.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)
    minutes = Column(Integer)
    contributor_id = Column(Integer)
    submitted = Column(Date)
    tags = Column(ARRAY(Text))
    nutrition = Column(JSONB)
    steps = Column(JSONB)
    description = Column(Text)
    image_url = Column(String(500))
