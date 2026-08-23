"""Tests for recipe API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.recipes import get_db
from tests.conftest import FakeDB, fake_recipes


@pytest.fixture()
def client():
    """TestClient with a mocked database."""
    db = FakeDB(fake_recipes())

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert "database" in body


class TestSearchRecipes:
    def test_search_returns_matching_recipes(self, client):
        resp = client.get("/recipes/search?q=chocolate")
        assert resp.status_code == 200
        body = resp.json()
        assert body["query"] == "chocolate"
        assert body["count"] >= 0
        assert "results" in body

    def test_search_rejects_empty_query(self, client):
        resp = client.get("/recipes/search?q=")
        assert resp.status_code == 422

    def test_search_rejects_missing_query(self, client):
        resp = client.get("/recipes/search")
        assert resp.status_code == 422

    def test_search_respects_limit(self, client):
        resp = client.get("/recipes/search?q=a&limit=1")
        assert resp.status_code == 200
        assert len(resp.json()["results"]) <= 1

    def test_search_rejects_invalid_limit(self, client):
        resp = client.get("/recipes/search?q=a&limit=0")
        assert resp.status_code == 422

    def test_search_rejects_limit_over_100(self, client):
        resp = client.get("/recipes/search?q=a&limit=101")
        assert resp.status_code == 422


class TestGetRecipe:
    def test_returns_recipe_detail(self, client):
        resp = client.get("/recipes/1")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == 1
        assert "name" in body
        assert "steps" in body
        assert "nutrition" in body
        assert "description" in body
        assert "tags" in body

    def test_recipe_detail_has_all_fields(self, client):
        resp = client.get("/recipes/1")
        body = resp.json()
        fields = ["id", "name", "minutes", "tags", "image_url", "description", "steps", "nutrition"]
        for field in fields:
            assert field in body, f"Missing field: {field}"


class TestListRecipes:
    def test_list_returns_recipes(self, client):
        resp = client.get("/recipes")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) > 0

    def test_list_respects_limit(self, client):
        resp = client.get("/recipes?limit=1")
        assert resp.status_code == 200
        assert len(resp.json()) <= 1

    def test_list_rejects_invalid_limit(self, client):
        resp = client.get("/recipes?limit=0")
        assert resp.status_code == 422

    def test_list_with_tag_filter(self, client):
        resp = client.get("/recipes?tag=dessert")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestListTags:
    def test_tags_returns_list(self, client):
        resp = client.get("/tags")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)

    def test_tags_respects_limit(self, client):
        resp = client.get("/tags?limit=1")
        assert resp.status_code == 200
        assert len(resp.json()) <= 1

    def test_tags_rejects_invalid_limit(self, client):
        resp = client.get("/tags?limit=0")
        assert resp.status_code == 422


class TestStats:
    def test_stats_returns_counts(self, client):
        resp = client.get("/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert "recipes" in body
        assert "recipes_with_image" in body
        assert isinstance(body["recipes"], int)
        assert isinstance(body["recipes_with_image"], int)
