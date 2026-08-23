# Frontend — Food Recommender App

Expo React Native app for searching and viewing recipes.

## Setup

```bash
npm install
```

## Running

```bash
npm start -- --web
```

Opens in your browser at http://localhost:8081.

To run on iOS/Android simulator, use `npm start` and scan the QR code with Expo Go.

## Configuration

Set the backend API URL (defaults to `http://localhost:8000`):

```bash
EXPO_PUBLIC_API_URL=http://localhost:8000
```

## Project Layout

```
frontend/
├── App.tsx                  Root component with navigation
├── src/
│   ├── api.ts               API client (searchRecipes, getRecipe)
│   ├── types.ts             TypeScript interfaces
│   └── screens/
│       ├── SearchScreen.tsx   Recipe search with results list
│       └── RecipeDetailScreen.tsx  Full recipe view
├── assets/                  App icons and splash
├── app.json                 Expo configuration
└── tsconfig.json            TypeScript config
```

## Features

- Search recipes by name or tags
- View recipe details (steps, nutrition, tags)
- Recipe images with placeholder fallback
- Back navigation between screens
