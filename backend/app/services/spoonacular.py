"""Spoonacular API client for recipe image enrichment."""

import re

import httpx

BASE_URL = "https://api.spoonacular.com"


class SpoonacularError(Exception):
    """Spoonacular API returned an unexpected response."""


class RateLimitError(SpoonacularError):
    """Daily or per-minute quota exhausted."""


def normalize_query(name: str) -> str:
    """Collapse whitespace so dataset names become usable search queries."""
    return re.sub(r"\s+", " ", name).strip()


class SpoonacularClient:
    def __init__(self, api_key: str, transport: httpx.BaseTransport | None = None):
        self._client = httpx.Client(
            base_url=BASE_URL,
            params={"apiKey": api_key},
            timeout=10.0,
            transport=transport,
        )

    def find_image(self, name: str) -> str | None:
        """Search for a recipe by name and return the best-matching image URL.

        Returns None when nothing matches; raises RateLimitError when the
        quota is exhausted so callers can stop instead of burning requests.
        """
        response = self._client.get(
            "/recipes/complexSearch",
            params={"query": normalize_query(name), "number": 3},
        )
        if response.status_code == 429:
            raise RateLimitError("Spoonacular quota exhausted (HTTP 429)")
        if response.status_code != 200:
            raise SpoonacularError(f"Spoonacular returned HTTP {response.status_code}")

        results = response.json().get("results", [])
        best = _pick_best_match(normalize_query(name), results)
        return best.get("image") if best else None


def _pick_best_match(query: str, results: list[dict]) -> dict | None:
    """Prefer an exact title match; otherwise take the first result."""
    if not results:
        return None
    for result in results:
        if normalize_query(result.get("title", "")).lower() == query.lower():
            return result
    return results[0]
