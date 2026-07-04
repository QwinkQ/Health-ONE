from __future__ import annotations

from app.core.schemas import NutritionFacts, Recipe
from app.services.data_store import get_ingredients


class NutritionService:
    def __init__(self) -> None:
        self.ingredients = get_ingredients()

    def calculate_recipe(self, recipe: Recipe, servings: int | None = None) -> NutritionFacts:
        target_servings = servings or recipe.servings
        scale = target_servings / recipe.servings
        total = NutritionFacts()

        for item in recipe.ingredients:
            ingredient = self.ingredients.get(item.name)
            if not ingredient:
                continue
            amount = item.amount_g * scale / 100
            total.calories += ingredient["calories_per_100g"] * amount
            total.protein_g += ingredient["protein_per_100g"] * amount
            total.fat_g += ingredient["fat_per_100g"] * amount
            total.carbs_g += ingredient["carbs_per_100g"] * amount
            total.fiber_g += ingredient["fiber_per_100g"] * amount
            total.sodium_mg += ingredient["sodium_mg_per_100g"] * amount

        return NutritionFacts(
            calories=round(total.calories, 1),
            protein_g=round(total.protein_g, 1),
            fat_g=round(total.fat_g, 1),
            carbs_g=round(total.carbs_g, 1),
            fiber_g=round(total.fiber_g, 1),
            sodium_mg=round(total.sodium_mg, 1),
        )

    def sum_nutrition(self, facts: list[NutritionFacts]) -> NutritionFacts:
        total = NutritionFacts()
        for item in facts:
            total.calories += item.calories
            total.protein_g += item.protein_g
            total.fat_g += item.fat_g
            total.carbs_g += item.carbs_g
            total.fiber_g += item.fiber_g
            total.sodium_mg += item.sodium_mg
        return NutritionFacts(
            calories=round(total.calories, 1),
            protein_g=round(total.protein_g, 1),
            fat_g=round(total.fat_g, 1),
            carbs_g=round(total.carbs_g, 1),
            fiber_g=round(total.fiber_g, 1),
            sodium_mg=round(total.sodium_mg, 1),
        )

