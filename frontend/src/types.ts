export interface RecipeSummary {
  id: number;
  name: string;
  minutes: number | null;
  tags: string[] | null;
  image_url: string | null;
}

export interface RecipeDetail extends RecipeSummary {
  description: string | null;
  steps: string[] | null;
  nutrition: Record<string, number> | null;
}

export interface SearchResponse {
  query: string;
  count: number;
  results: RecipeSummary[];
}
