"""Shared test fixtures."""

from unittest.mock import MagicMock


def fake_recipes():
    """Return a list of mock Recipe ORM objects."""
    recipes = []
    data = [
        {
            "id": 1,
            "name": "Chocolate Chip Cookies",
            "minutes": 45,
            "tags": ["dessert", "baking", "cookies"],
            "image_url": "https://img.example.com/cookies.jpg",
            "description": "Classic chocolate chip cookies.",
            "steps": ["Mix ingredients.", "Bake at 350F for 12 minutes."],
            "nutrition": {
                "calories": 200,
                "total_fat": 10,
                "sugar": 12,
                "sodium": 150,
                "protein": 3,
                "saturated_fat": 5,
                "carbs": 28,
            },
        },
        {
            "id": 2,
            "name": "Pancakes",
            "minutes": 20,
            "tags": ["breakfast", "quick"],
            "image_url": "",
            "description": "Fluffy breakfast pancakes.",
            "steps": ["Mix batter.", "Cook on griddle."],
            "nutrition": {
                "calories": 350, "total_fat": 8, "sugar": 6,
                "sodium": 400, "protein": 9, "saturated_fat": 2, "carbs": 60,
            },
        },
        {
            "id": 3,
            "name": "Chicken Stir Fry",
            "minutes": 30,
            "tags": ["dinner", "asian", "quick"],
            "image_url": "https://img.example.com/stirfry.jpg",
            "description": "Quick chicken stir fry with vegetables.",
            "steps": ["Cut chicken.", "Stir fry vegetables.", "Add sauce."],
            "nutrition": {
                "calories": 400, "total_fat": 15, "sugar": 8,
                "sodium": 600, "protein": 35, "saturated_fat": 3, "carbs": 25,
            },
        },
    ]
    for d in data:
        obj = MagicMock()
        for k, v in d.items():
            setattr(obj, k, v)
        recipes.append(obj)
    return recipes


class FakeQuery:
    """Mimics a SQLAlchemy query for testing."""

    def __init__(self, recipes):
        self._recipes = list(recipes)
        self._filters = []
        self._limit_val = None
        self._offset_val = 0
        self._order = None

    def filter(self, *args):
        self._filters.extend(args)
        return self

    def any(self, *args):
        return True

    def ilike(self, pattern):
        return True

    def limit(self, n):
        self._limit_val = n
        return self

    def offset(self, n):
        self._offset_val = n
        return self

    def order_by(self, *args):
        self._order = args
        return self

    def group_by(self, *args):
        self._group = args
        return self

    def all(self):
        if hasattr(self, "_group"):
            return self._build_tag_counts()
        result = self._recipes
        if self._limit_val is not None:
            result = result[: self._limit_val]
        return result

    def _build_tag_counts(self):
        counts: dict[str, int] = {}
        for r in self._recipes:
            for tag in (r.tags or []):
                counts[tag] = counts.get(tag, 0) + 1
        rows = []
        for tag, count in sorted(counts.items(), key=lambda x: -x[1]):
            obj = MagicMock()
            obj.tag = tag
            obj.count = count
            rows.append(obj)
        if self._limit_val is not None:
            rows = rows[: self._limit_val]
        return rows

    def first(self):
        return self._recipes[0] if self._recipes else None

    def scalar(self):
        return len(self._recipes)


class FakeDB:
    """Mimics a SQLAlchemy Session for testing."""

    def __init__(self, recipes):
        self._recipes = recipes

    def query(self, *args, **kwargs):
        return FakeQuery(self._recipes)

    def close(self):
        pass


def make_recipe_mock(**overrides):
    """Create a single mock Recipe ORM object."""
    defaults = {
        "id": 1,
        "name": "Test Recipe",
        "minutes": 30,
        "tags": ["test"],
        "image_url": None,
        "description": "A test recipe.",
        "steps": ["Step 1."],
        "nutrition": {"calories": 100},
    }
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj
