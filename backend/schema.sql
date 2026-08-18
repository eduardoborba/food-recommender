-- Food Recommender Database Schema
-- PostgreSQL + pgvector

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Ingredients: normalized lookup table
CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_ingredients_name ON ingredients USING gin (name gin_trgm_ops);

-- Recipes: from Food.com dataset
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,  -- original dataset ID
    name VARCHAR(500) NOT NULL,
    minutes INTEGER,
    contributor_id INTEGER,
    submitted DATE,
    tags TEXT[],
    nutrition JSONB,
    steps JSONB,
    description TEXT,
    image_url TEXT,
    embedding VECTOR(512),  -- TF-IDF vector, populated by ML pipeline
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_recipes_name ON recipes USING gin (name gin_trgm_ops);
CREATE INDEX idx_recipes_tags ON recipes USING gin (tags);
CREATE INDEX idx_recipes_embedding ON recipes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Recipe ↔ Ingredient junction
CREATE TABLE recipe_ingredients (
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE CASCADE,
    quantity TEXT,  -- original text from dataset, e.g. "2 cups"
    PRIMARY KEY (recipe_id, ingredient_id)
);

-- Users (added in Phase 2, schema here for reference)
-- CREATE TABLE users (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     email VARCHAR(255) UNIQUE NOT NULL,
--     password_hash VARCHAR(255) NOT NULL,
--     preferences JSONB DEFAULT '{}',
--     created_at TIMESTAMPTZ DEFAULT now()
-- );

-- User ↔ Ingredient (pantry, added in Phase 4)
-- CREATE TABLE user_pantry (
--     user_id UUID REFERENCES users(id) ON DELETE CASCADE,
--     ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE CASCADE,
--     added_at TIMESTAMPTZ DEFAULT now(),
--     PRIMARY KEY (user_id, ingredient_id)
-- );

-- User interactions (ratings + favorites, added in Phase 2)
-- CREATE TABLE user_interactions (
--     user_id UUID REFERENCES users(id) ON DELETE CASCADE,
--     recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
--     rating INTEGER CHECK (rating >= 1 AND rating <= 5),
--     favorite BOOLEAN DEFAULT FALSE,
--     created_at TIMESTAMPTZ DEFAULT now(),
--     UNIQUE (user_id, recipe_id)
-- );
