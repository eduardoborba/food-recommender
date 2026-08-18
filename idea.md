Building an ingredient-aware recipe recommender system using the Food.com Kaggle dataset (RAW_recipes.csv and RAW_interactions.csv) requires a hybrid recommendation model combining TF-IDF vector similarity for pantry matching with Collaborative Filtering for user preferences.
Technology Stack
Mobile Frontend: Flutter or React Native (Cross-platform UI).
Backend API: FastAPI (Python) for asynchronous endpoints and ML model serving.
Database & Search: PostgreSQL + pgvector (stores relational user profiles, recipe metadata, and pre-computed vector embeddings).
ML Engine: Scikit-Learn (TF-IDF vectorizer + Cosine Similarity) and PyTorch / Surprise (Implicit Collaborative Filtering).
System Architecture & Recommendation Logic
Pantry Filtering (Content-Based): Convert available pantry items into sparse TF-IDF vectors matching recipe ingredient tokens. Calculate cosine similarity to rank recipes by ingredient overlap percentage.
Preference Reranking (Collaborative Filtering): Re-rank the top pantry matches using matrix factorization based on the user's historical ratings, dietary tags, and favorited categories.
Data Models
+-------------------+      +-----------------------+      +-------------------+
|       User        |      |      UserPantry       |      |     Ingredient    |
+-------------------+      +-----------------------+      +-------------------+
| id: UUID          | <--->| user_id: UUID (FK)    |      | id: INT           |
| email: VARCHAR    |      | ingredient_id: INT(FK)| <--->| name: VARCHAR     |
| preferences: JSONB|      +-----------------------+      +-------------------+
+-------------------+

+-------------------+      +-----------------------+      +-------------------+
|      Recipe       |      |    RecipeIngredient   |      |    UserInteraction|
+-------------------+      +-----------------------+      +-------------------+
| id: INT           | <--->| recipe_id: INT (FK)   |      | user_id: UUID (FK)|
| name: VARCHAR     |      | ingredient_id: INT(FK)|      | recipe_id: INT(FK)|
| steps: JSONB      |      +-----------------------+      | rating: INT       |
| tags: TEXT[]      |                                     | favorite: BOOL    |
| embeddings: VECTOR|                                     +-------------------+
+-------------------+

User: Stores credentials and dietary preference tags (e.g., ["vegan", "low-carb"]).
Recipe: Mapped directly from RAW_recipes.csv (id, name, minutes, steps, nutrition, tags).
Ingredient: Normalized lookup table extracted from ingredients array column.
UserPantry: Junction table tracking ingredients currently marked as available by the user.
UserInteraction: Historical ratings and favorites sourced initially from RAW_interactions.csv for initial model training.
Main Mobile App Pages
Pantry / Fridge Inventory: Multi-select interface with autocomplete to add/remove available ingredients. Includes toggle switches for common staples (salt, oil, water).
Discover / Feed: Recommendations feed displaying recipes ranked by match percentage (e.g., "95% match - You have 6/7 ingredients"). Filters for max prep time, diet type, and missing ingredient count.
Recipe View: Step-by-step instructions, nutrition breakdown, missing ingredient highlights, and a rating/review submit section.
Profile & Preferences: Manage saved favorite recipes, set macro targets, and define blacklist ingredients (allergies/dislikes).
