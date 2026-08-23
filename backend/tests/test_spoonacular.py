"""Tests for the Spoonacular image-enrichment client."""

import httpx
import pytest

from app.services.spoonacular import RateLimitError, SpoonacularClient


def make_client(handler) -> SpoonacularClient:
    transport = httpx.MockTransport(handler)
    return SpoonacularClient(api_key="test-key", transport=transport)


def search_response(results):
    return httpx.Response(200, json={"results": results})


class TestFindImage:
    def test_returns_image_of_exact_title_match(self):
        def handler(request):
            return search_response([
                {"id": 1, "title": "Best Chocolate Chip Cookies", "image": "https://img/1.jpg"},
                {"id": 2, "title": "chocolate chip cookies", "image": "https://img/2.jpg"},
            ])

        client = make_client(handler)
        assert client.find_image("Chocolate Chip Cookies") == "https://img/2.jpg"

    def test_sends_normalized_query_and_api_key(self):
        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            return search_response([])

        client = make_client(handler)
        client.find_image("  Chocolate   Chip Cookies ")
        assert captured["url"].startswith("https://api.spoonacular.com/recipes/complexSearch")
        assert "apiKey=test-key" in captured["url"]

    def test_falls_back_to_first_result_without_exact_match(self):
        def handler(request):
            return search_response([
                {"id": 1, "title": "Easy Pancakes", "image": "https://img/easy.jpg"},
                {"id": 2, "title": "Fluffy Pancakes", "image": "https://img/fluffy.jpg"},
            ])

        client = make_client(handler)
        assert client.find_image("Pancakes") == "https://img/easy.jpg"

    def test_returns_none_when_no_results(self):
        client = make_client(lambda request: search_response([]))
        assert client.find_image("zzz nonexistent dish zzz") is None

    def test_returns_none_when_results_lack_images(self):
        def handler(request):
            return search_response([{"id": 1, "title": "Mystery Dish"}])

        client = make_client(handler)
        assert client.find_image("Mystery Dish") is None

    def test_raises_rate_limit_error_on_429(self):
        def handler(request):
            return httpx.Response(429, json={"message": "limit reached"})

        client = make_client(handler)
        with pytest.raises(RateLimitError):
            client.find_image("Pancakes")
