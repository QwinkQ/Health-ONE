from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Goal = Literal["cutting", "bulking", "maintaining"]


class IngredientAmount(BaseModel):
    name: str
    amount_g: float = Field(ge=0)
    optional: bool = False


class NutritionFacts(BaseModel):
    calories: float = 0
    protein_g: float = 0
    fat_g: float = 0
    carbs_g: float = 0
    fiber_g: float = 0
    sodium_mg: float = 0


class Recipe(BaseModel):
    id: str
    name: str
    cuisine: str
    taste_tags: list[str]
    difficulty: str
    cooking_time_min: int
    servings: int
    ingredients: list[IngredientAmount]
    steps: list[str]
    goals: list[Goal] = []
    suitable_conditions: list[str] = []
    avoid_conditions: list[str] = []
    forbidden_ingredients: list[str] = []
    tips: str = ""


class RecipeSearchRequest(BaseModel):
    query: str | None = None
    ingredients: list[str] = []
    avoid_ingredients: list[str] = []
    conditions: list[str] = []
    max_time_min: int | None = None
    goal: Goal | None = None
    limit: int = Field(default=5, ge=1, le=20)


class RecipeCandidate(BaseModel):
    recipe: Recipe
    score: float
    matched_ingredients: list[str]
    missing_ingredients: list[IngredientAmount]
    warnings: list[str]
    nutrition: NutritionFacts


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    recipes: list[RecipeCandidate]
    shopping_list: list[IngredientAmount]
    nutrition_summary: NutritionFacts
    warnings: list[str]
    parsed_context: dict


class InventoryItem(BaseModel):
    name: str
    amount_g: float = Field(ge=0)
    location: str = "fridge"
    expiry_date: str | None = None


class InventoryUpsertRequest(BaseModel):
    items: list[InventoryItem]


class NutritionCalculateRequest(BaseModel):
    recipe_id: str
    servings: int = Field(default=1, ge=1)
    substitutions: list[dict[str, str | float]] = []


class ShoppingListRequest(BaseModel):
    recipe_ids: list[str]
    inventory: list[InventoryItem] = []


class HealthDailyLog(BaseModel):
    user_id: str
    date: str
    provider: str = "health_connect"
    steps: int = Field(default=0, ge=0)
    active_energy_kcal: float = Field(default=0, ge=0)
    workout_energy_kcal: float = Field(default=0, ge=0)
    workout_type: str | None = None
    workout_duration_min: int = Field(default=0, ge=0)
    body_weight_kg: float | None = Field(default=None, ge=0)
    sleep_minutes: int | None = Field(default=None, ge=0)
    synced_at: str | None = None


class HealthConnectDailySyncRequest(BaseModel):
    user_id: str
    date: str
    timezone: str = "Asia/Shanghai"
    steps: int = Field(default=0, ge=0)
    active_energy_kcal: float = Field(default=0, ge=0)
    workout_energy_kcal: float = Field(default=0, ge=0)
    workout_type: str | None = None
    workout_duration_min: int = Field(default=0, ge=0)
    body_weight_kg: float | None = Field(default=None, ge=0)
    sleep_minutes: int | None = Field(default=None, ge=0)


class HealthSummaryResponse(BaseModel):
    user_id: str
    latest_log: HealthDailyLog | None = None
    target_adjustment: dict[str, float | str] = {}
    message: str
