# Backend — Food Recommender API

FastAPI application serving recipe search, detail, and recommendation endpoints.

## Setup

```bash
pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and add your Spoonacular API key for image enrichment.

## Running

```bash
uvicorn app.main:app --reload --port 8000
```

API documentation: http://localhost:8000/docs

## Database

Requires PostgreSQL with pgvector. Start with Docker Compose from the project root:

```bash
docker compose up -d
```

The schema is auto-applied from `schema.sql` on first boot.

### Import dataset

```bash
python -m scripts.import_dataset --csv-dir ../data/raw
```

### Enrich images

```bash
python -m scripts.enrich_images --limit 50
```

## Testing

```bash
pytest
```

## Linting

```bash
ruff check .
```

## Project Layout

```
backend/
├── app/
│   ├── main.py            FastAPI entry point
│   ├── config.py          Settings from .env
│   ├── database.py        SQLAlchemy engine
│   ├── models.py          ORM models
│   ├── schemas.py         Pydantic response schemas
│   ├── routers/
│   │   └── recipes.py     All recipe endpoints
│   └── services/
│       └── spoonacular.py Spoonacular API client
├── scripts/
│   ├── import_dataset.py  CSV → PostgreSQL import
│   └── enrich_images.py   Batch image fetching
├── tests/
│   ├── conftest.py        Test fixtures and mocks
│   ├── test_api.py        Endpoint tests
│   ├── test_schemas.py    Schema validation tests
│   └── test_spoonacular.py  API client tests
├── schema.sql             Database schema
├── pyproject.toml         Project config
└── .env                   Environment variables
```
