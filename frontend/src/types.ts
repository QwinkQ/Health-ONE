export type IngredientAmount = {
  name: string;
  amount_g: number;
  optional?: boolean;
};

export type NutritionFacts = {
  calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
  fiber_g: number;
  sodium_mg: number;
};

export type Recipe = {
  id: string;
  name: string;
  cuisine: string;
  taste_tags: string[];
  difficulty: string;
  cooking_time_min: number;
  servings: number;
  ingredients: IngredientAmount[];
  steps: string[];
  tips: string;
};

export type RecipeCandidate = {
  recipe: Recipe;
  score: number;
  matched_ingredients: string[];
  missing_ingredients: IngredientAmount[];
  warnings: string[];
  nutrition: NutritionFacts;
};

export type ChatResponse = {
  answer: string;
  recipes: RecipeCandidate[];
  shopping_list: IngredientAmount[];
  nutrition_summary: NutritionFacts;
  warnings: string[];
  parsed_context: Record<string, unknown>;
};

