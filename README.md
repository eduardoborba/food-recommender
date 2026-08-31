# Food Recommender

An ingredient-aware recipe recommender that matches what you have in your pantry to what you can cook, refined by your taste history.

Built with the [Food.com dataset](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions) (231K recipes).

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React Native (Expo) |
| Backend API | FastAPI (Python 3.12+) |
| Database | PostgreSQL + pgvector |
| ML Engine | scikit-learn, implicit |

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker (for PostgreSQL)

### 1. Start the database

```bash
docker compose up -d
```

### 2. Import the dataset

Place `RAW_recipes.csv` and `RAW_interactions.csv` in `data/raw/`, then:

```bash
cd backend
python -m scripts.import_dataset --csv-dir ../data/raw
```

### 3. Run the backend API

```bash
cd backend
pip install -e .
uvicorn app.main:app --reload --port 8000
```

API docs at http://localhost:8000/docs.

### 4. Run the mobile app

```bash
cd frontend
npm install
npm start -- --web
```

Opens in your browser at http://localhost:8081.

### 5. (Optional) Enrich with recipe images

Set your Spoonacular API key in `backend/.env`, then:

```bash
cd backend
python -m scripts.enrich_images --limit 50
```

## Project Structure

```
food-recommender/
├── backend/           FastAPI application
│   ├── app/           API routes, models, schemas
│   ├── scripts/       Import and enrichment CLI tools
│   └── tests/         Pytest test suite
├── frontend/          Expo React Native app
│   ├── src/           Screens, API client, types
│   └── assets/        App icons and splash
├── data/raw/          Food.com CSV dataset files
├── docs/              Architecture decision records
├── docker-compose.yml PostgreSQL + pgvector
└── idea.md            Full product spec
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/recipes/search?q=...` | Search recipes by name or tags |
| GET | `/recipes/{id}` | Get full recipe details |
| GET | `/recipes` | List recipes (optional `?tag=` filter) |
| GET | `/tags` | List most common recipe tags |
| GET | `/stats` | Database statistics |
| GET | `/health` | Health check |

## Development

```bash
# Lint
cd backend && ruff check .

# Test
cd backend && pytest

# Type check frontend
cd frontend && npx tsc --noEmit
```

## Roadmap

- [x] Phase 1: Data foundation, search API, Expo skeleton, image enrichment
- [ ] Phase 2: User accounts and profiles
- [ ] Phase 3: Recommendation engine (TF-IDF + collaborative filtering)
- [ ] Phase 4: Pantry management and advanced filtering
