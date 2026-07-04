from __future__ import annotations

from app.core.schemas import RecipeCandidate, RecipeSearchRequest
from app.services.data_store import get_recipes
from app.services.inventory_service import InventoryService
from app.services.nutrition_service import NutritionService
from app.services.safety_rule_service import SafetyRuleService


class RagService:
    """MVP recipe retrieval.

    This is a deterministic metadata + lexical retriever. Replace this service
    with Chroma, pgvector, Qdrant, or Milvus when the recipe corpus grows.
    """

    def __init__(self) -> None:
        self.recipes = get_recipes()
        self.nutrition = NutritionService()
        self.inventory = InventoryService()
        self.safety = SafetyRuleService()

    def search(self, request: RecipeSearchRequest) -> list[RecipeCandidate]:
        inventory_names = set(request.ingredients)
        avoid = set(request.avoid_ingredients)
        candidates: list[RecipeCandidate] = []

        for recipe in self.recipes:
            if request.max_time_min and recipe.cooking_time_min > request.max_time_min:
                continue
            if request.goal and request.goal not in recipe.goals:
                continue
            if avoid.intersection({item.name for item in recipe.ingredients if not item.optional}):
                continue

            nutrition = self.nutrition.calculate_recipe(recipe)
            warnings = self.safety.evaluate_recipe(recipe, nutrition, request.conditions, request.avoid_ingredients)
            matched = self.inventory.matched_names(recipe, inventory_names)
            missing = self.inventory.missing_for_recipe(recipe, inventory_names)

            score = self._score(recipe, request, matched, missing, warnings)
            if score <= 0:
                continue

            candidates.append(
                RecipeCandidate(
                    recipe=recipe,
                    score=round(score, 3),
                    matched_ingredients=matched,
                    missing_ingredients=missing,
                    warnings=warnings,
                    nutrition=nutrition,
                )
            )

        return sorted(candidates, key=lambda item: item.score, reverse=True)[: request.limit]

    def _score(self, recipe, request: RecipeSearchRequest, matched: list[str], missing: list, warnings: list[str]) -> float:
        score = 1.0
        score += len(matched) * 2.0
        score -= len(missing) * 0.5
        score -= len(warnings) * 0.2

        if request.query:
            query = request.query
            text = " ".join(
                [
                    recipe.name,
                    recipe.cuisine,
                    " ".join(recipe.taste_tags),
                    " ".join(step for step in recipe.steps),
                    recipe.tips,
                ]
            )
            for token in [query, "清淡", "高蛋白", "轻盐", "低脂", "老人"]:
                if token and token in text:
                    score += 0.6

        if "hypertension" in request.conditions and "hypertension" in recipe.suitable_conditions:
            score += 1.0
        if "elderly" in request.conditions and "elderly" in recipe.suitable_conditions:
            score += 0.6
        if request.goal and request.goal in recipe.goals:
            score += 0.8

        return score

