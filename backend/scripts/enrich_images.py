"""Enrich recipes with images from the Spoonacular API.

Usage:
    cd backend
    python -m scripts.enrich_images --limit 50

Requires SPOONACULAR_API_KEY in backend/.env. The free tier allows a small
number of requests per day, so always pass --limit and check /stats after.
"""

import argparse
import sys
import time

import psycopg2

from app.config import settings
from app.services.spoonacular import RateLimitError, SpoonacularClient


def fetch_pending(cur, limit: int) -> list[tuple[int, str]]:
    cur.execute(
        "SELECT id, name FROM recipes WHERE image_url IS NULL ORDER BY id LIMIT %s",
        (limit,),
    )
    return cur.fetchall()


def enrich(conn, client: SpoonacularClient, limit: int) -> int:
    cur = conn.cursor()
    pending = fetch_pending(cur, limit)
    print(f"Enriching {len(pending)} recipes...")

    updated = 0
    for recipe_id, name in pending:
        try:
            image_url = client.find_image(name)
        except RateLimitError:
            print(f"\nQuota exhausted after {updated} updates — stopping early.")
            break

        if image_url:
            cur.execute(
                "UPDATE recipes SET image_url = %s WHERE id = %s",
                (image_url, recipe_id),
            )
            updated += 1
        else:
            # Mark as checked so we never re-query hopeless names.
            cur.execute(
                "UPDATE recipes SET image_url = '' WHERE id = %s",
                (recipe_id,),
            )

        conn.commit()
        if (updated + 1) % 10 == 0:
            print(f"  ... {updated + 1}/{len(pending)} processed", flush=True)
        time.sleep(1.1)  # stay under the per-second rate limit

    return updated


def main():
    parser = argparse.ArgumentParser(description="Fetch recipe images from Spoonacular")
    parser.add_argument("--limit", type=int, default=10, help="Max recipes to process this run")
    parser.add_argument(
        "--db-url", type=str,
        default="postgresql://food:food@localhost:5433/food_recommender",
    )
    args = parser.parse_args()

    if not settings.spoonacular_api_key:
        print("Error: SPOONACULAR_API_KEY not set (add it to backend/.env)")
        sys.exit(1)

    conn = psycopg2.connect(args.db_url)
    client = SpoonacularClient(api_key=settings.spoonacular_api_key)

    try:
        updated = enrich(conn, client, args.limit)
        print(f"Done: {updated} recipes enriched.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
