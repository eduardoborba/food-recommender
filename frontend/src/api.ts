import type { RecipeDetail, SearchResponse } from './types';

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API error ${response.status}: ${path}`);
  }
  return response.json() as Promise<T>;
}

export function searchRecipes(query: string, limit = 20): Promise<SearchResponse> {
  return request<SearchResponse>(
    `/recipes/search?q=${encodeURIComponent(query)}&limit=${limit}`,
  );
}

export function getRecipe(id: number): Promise<RecipeDetail> {
  return request<RecipeDetail>(`/recipes/${id}`);
}
