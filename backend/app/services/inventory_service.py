from __future__ import annotations

from collections import defaultdict

from app.core.schemas import IngredientAmount, InventoryItem, Recipe


class InventoryService:
    def missing_for_recipes(
        self,
        recipes: list[Recipe],
        inventory: list[InventoryItem],
    ) -> list[IngredientAmount]:
        available = defaultdict(float)
        for item in inventory:
            available[item.name] += item.amount_g

        required = defaultdict(float)
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                if ingredient.optional:
                    continue
                required[ingredient.name] += ingredient.amount_g

        missing: list[IngredientAmount] = []
        for name, amount_g in required.items():
            shortage = amount_g - available.get(name, 0)
            if shortage > 0:
                missing.append(IngredientAmount(name=name, amount_g=round(shortage, 1)))

        return missing

    def matched_names(self, recipe: Recipe, inventory_names: set[str]) -> list[str]:
        return [item.name for item in recipe.ingredients if item.name in inventory_names]

    def missing_for_recipe(self, recipe: Recipe, inventory_names: set[str]) -> list[IngredientAmount]:
        return [
            IngredientAmount(name=item.name, amount_g=item.amount_g, optional=item.optional)
            for item in recipe.ingredients
            if item.name not in inventory_names and not item.optional
        ]

