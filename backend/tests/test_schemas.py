"""Tests for API response schemas."""

from app.schemas import RecipeDetail, RecipeSummary


class FakeRecipe:
    """Mimics ORM attribute access for from_attributes validation."""

    id = 1
    name = "Test Recipe"
    minutes = 30
    tags = ["dessert"]
    description = None
    steps = []
    nutrition = None
    image_url = ""


class TestImageUrlNormalization:
    def test_checked_but_imageless_recipe_serializes_without_image(self):
        summary = RecipeSummary.model_validate(FakeRecipe())
        assert summary.image_url is None

    def test_detail_inherits_normalization(self):
        detail = RecipeDetail.model_validate(FakeRecipe())
        assert detail.image_url is None
