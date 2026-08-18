"""Import Food.com dataset into PostgreSQL.

Usage:
    cd backend
    python -m scripts.import_dataset --csv-dir ../data/raw
"""

import argparse
import ast
import csv
import json
import re
import sys
import time
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values


def parse_minutes(val: str) -> int | None:
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def parse_list_field(val: str) -> list[str] | None:
    """Parse a stringified Python list like "['tag1', 'tag2']"."""
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (ValueError, SyntaxError):
        pass
    return None


def parse_nutrition(val: str) -> dict | None:
    """Parse nutrition string like '[calories, fat, ...]' into a dict."""
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, list) and len(parsed) >= 7:
            keys = ["calories", "total_fat", "sugar", "sodium", "protein", "saturated_fat", "carbs"]
            return {k: float(v) for k, v in zip(keys, parsed)}
    except (ValueError, SyntaxError):
        pass
    return None


def normalize_ingredient(name: str) -> str:
    """Lowercase, strip whitespace, remove parenthetical descriptions."""
    name = name.strip().lower()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\(.*?\)", "", name).strip()
    return name


def load_recipes(csv_path: Path) -> list[tuple]:
    """Load recipes from RAW_recipes.csv."""
    recipes = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            recipe_id = int(row["id"])
            name = row["name"].strip()
            minutes = parse_minutes(row.get("minutes", ""))
            contributor_id = int(row["contributor_id"]) if row.get("contributor_id") else None
            submitted = row.get("submitted") or None
            tags = parse_list_field(row.get("tags", "[]"))
            nutrition = parse_nutrition(row.get("nutrition", "[]"))
            steps = parse_list_field(row.get("steps", "[]"))
            description = row.get("description", "").strip() or None

            recipes.append((
                recipe_id, name, minutes, contributor_id,
                submitted, tags, json.dumps(nutrition), json.dumps(steps), description,
            ))
            if (i + 1) % 10000 == 0:
                print(f"  ... loaded {i + 1} recipes", flush=True)
    return recipes


def load_ingredients_from_recipes(csv_path: Path) -> dict[str, set[int]]:
    """Extract all unique ingredients and which recipes use them."""
    ingredient_map: dict[str, set[int]] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            recipe_id = int(row["id"])
            raw_ingredients = parse_list_field(row.get("ingredients", "[]")) or []
            for ing in raw_ingredients:
                normalized = normalize_ingredient(ing)
                if normalized:
                    if normalized not in ingredient_map:
                        ingredient_map[normalized] = set()
                    ingredient_map[normalized].add(recipe_id)
            if (i + 1) % 10000 == 0:
                print(f"  ... scanned {i + 1} recipes", flush=True)
    return ingredient_map


def import_to_database(conn, recipes: list[tuple], ingredient_map: dict[str, set[int]]):
    """Insert recipes and ingredients into PostgreSQL."""
    cur = conn.cursor()

    # Insert recipes
    print(f"Inserting {len(recipes)} recipes...")
    t0 = time.time()
    insert_recipes = """
        INSERT INTO recipes (id, name, minutes, contributor_id, submitted, tags, nutrition, steps, description)
        VALUES %s
        ON CONFLICT (id) DO NOTHING
    """
    execute_values(cur, insert_recipes, recipes, page_size=1000)
    conn.commit()
    print(f"  -> {cur.rowcount} recipes inserted ({time.time() - t0:.1f}s)")

    # Insert ingredients
    ingredient_names = sorted(ingredient_map.keys())
    print(f"Inserting {len(ingredient_names)} unique ingredients...")
    t0 = time.time()
    ingredient_ids = {}
    for name in ingredient_names:
        cur.execute(
            "INSERT INTO ingredients (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id",
            (name,),
        )
        result = cur.fetchone()
        if result:
            ingredient_ids[name] = result[0]
        else:
            cur.execute("SELECT id FROM ingredients WHERE name = %s", (name,))
            ingredient_ids[name] = cur.fetchone()[0]

    conn.commit()
    print(f"  -> {len(ingredient_ids)} ingredients resolved ({time.time() - t0:.1f}s)")

    # Insert recipe_ingredients junction
    print("Linking recipes to ingredients...")
    t0 = time.time()
    junction_data = []
    for ing_name, recipe_ids in ingredient_map.items():
        ing_id = ingredient_ids.get(ing_name)
        if ing_id:
            for recipe_id in recipe_ids:
                junction_data.append((recipe_id, ing_id))

    insert_junction = """
        INSERT INTO recipe_ingredients (recipe_id, ingredient_id)
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    execute_values(cur, insert_junction, junction_data, page_size=5000)
    conn.commit()
    print(f"  -> {cur.rowcount} recipe-ingredient links created ({time.time() - t0:.1f}s)")


def main():
    parser = argparse.ArgumentParser(description="Import Food.com dataset")
    parser.add_argument("--csv-dir", type=Path, required=True, help="Directory containing RAW_recipes.csv")
    parser.add_argument("--db-url", type=str, default="postgresql://food:food@localhost:5433/food_recommender")
    args = parser.parse_args()

    csv_dir = args.csv_dir
    recipes_csv = csv_dir / "RAW_recipes.csv"

    if not recipes_csv.exists():
        print(f"Error: {recipes_csv} not found")
        sys.exit(1)

    t_start = time.time()
    print(f"Loading recipes from {recipes_csv}...")
    recipes = load_recipes(recipes_csv)
    print(f"  -> {len(recipes)} recipes loaded")

    print("Extracting ingredients...")
    ingredient_map = load_ingredients_from_recipes(recipes_csv)
    print(f"  -> {len(ingredient_map)} unique ingredients found")

    print(f"Connecting to database...")
    conn = psycopg2.connect(args.db_url)

    try:
        import_to_database(conn, recipes, ingredient_map)
        elapsed = time.time() - t_start
        print(f"\nImport complete! ({elapsed:.1f}s total)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
