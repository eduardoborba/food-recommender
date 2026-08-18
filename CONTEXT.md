# Food Recommender

An ingredient-aware recipe recommender that matches what you have in your pantry to what you can cook, refined by your taste history.

## Language

### Core Concepts

**Recipe**:
A named collection of ingredients, steps, tags, and nutritional metadata, sourced from the Food.com dataset and enriched with images.
_Avoid_: meal, dish, item

**Ingredient**:
A normalized food item (e.g. "chicken breast", "olive oil") that appears in one or more recipes. Stored in a lookup table; recipes reference ingredients by ID.
_Aavoid_: component, item, food

**User**:
A person with an account, dietary preferences, and a history of interactions (ratings, favorites).
_Avoid_: customer, account, person

**Pantry**:
A user's manually curated list of ingredients they currently have available. No expiry tracking. Users add/remove items; the system filters recipes by overlap.
_Avoid_: fridge, inventory, cabinet

### Interactions

**Interaction**:
A recorded user action on a recipe — either a numeric rating (1-5) or a boolean favorite. Used to train the collaborative filtering model.
_Avoid_: feedback, review, action

**Rating**:
A 1-5 integer score a user assigns to a recipe after cooking it.
_Avoid_: stars, score

**Favorite**:
A boolean flag indicating a user wants to save or revisit a recipe. Distinct from a rating — a recipe can be favorited without being rated.
_Avoid_: save, bookmark, like

### Matching

**Match Percentage**:
The ratio of overlapping ingredients between a user's pantry and a recipe's required ingredients, expressed as a percentage. Simple count-based: (pantry ingredients ∩ recipe ingredients) / (recipe ingredients).
_Avoid_: score, similarity, overlap

**Blacklisted Ingredient**:
An ingredient a user never wants in their recipes — covers both allergies and dislikes with equal severity. Recipes containing any blacklisted ingredient are excluded from results.
_Avoid_: excluded, blocked, forbidden

### Data Enrichment

**Enrichment**:
The process of augmenting raw dataset fields with external data — specifically, fetching recipe images from the Spoonacular API after initial import.
_Avoid_: augmentation, supplement
