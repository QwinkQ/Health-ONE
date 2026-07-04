from __future__ import annotations

from app.core.schemas import NutritionFacts, Recipe
from app.services.data_store import get_safety_rules


class SafetyRuleService:
    def __init__(self) -> None:
        self.rules = get_safety_rules()

    def evaluate_recipe(
        self,
        recipe: Recipe,
        nutrition: NutritionFacts,
        conditions: list[str],
        avoid_ingredients: list[str],
    ) -> list[str]:
        warnings: list[str] = []
        recipe_ingredient_names = {item.name for item in recipe.ingredients}

        for forbidden in avoid_ingredients:
            if forbidden in recipe_ingredient_names or forbidden in recipe.forbidden_ingredients:
                warnings.append(f"已检测到忌口食材：{forbidden}，建议删除或替换。")

        if "hypertension" in conditions:
            if nutrition.sodium_mg > 700:
                warnings.append("该菜钠含量偏高，高血压用户建议减少盐和生抽。")
            if "盐" in recipe_ingredient_names or "生抽" in recipe_ingredient_names:
                warnings.append("高血压场景建议低盐烹饪，优先蒸、煮、炖。")

        if "diabetes" in conditions and nutrition.carbs_g > 80:
            warnings.append("糖尿病用户需要注意本餐碳水较高，建议控制主食份量。")

        if "kidney_disease" in conditions and "菠菜" in recipe_ingredient_names:
            warnings.append("肾病用户对菠菜等高钾食材需谨慎，建议咨询医生或营养师。")

        if "elderly" in conditions and recipe.difficulty == "中等":
            warnings.append("老人食用建议做得更软烂，避免过硬、过辣、过烫。")

        return warnings

    def summarize_conditions(self, conditions: list[str]) -> list[str]:
        messages: list[str] = []
        for condition in conditions:
            rule = self.rules.get(condition)
            if rule:
                messages.extend(rule["rules"])
        return messages

