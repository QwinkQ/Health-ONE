from __future__ import annotations

import re

from app.core.schemas import ChatResponse, IngredientAmount, InventoryItem, NutritionFacts, RecipeSearchRequest
from app.services.data_store import get_ingredients
from app.services.inventory_service import InventoryService
from app.services.nutrition_service import NutritionService
from app.services.rag_service import RagService
from app.services.safety_rule_service import SafetyRuleService


class AgentService:
    def __init__(self) -> None:
        self.rag = RagService()
        self.inventory = InventoryService()
        self.nutrition = NutritionService()
        self.safety = SafetyRuleService()
        self.ingredients = get_ingredients()

    def handle_chat(self, user_id: str, message: str) -> ChatResponse:
        context = self._parse_message(user_id, message)
        search_request = RecipeSearchRequest(
            query=message,
            ingredients=context["ingredients"],
            avoid_ingredients=context["avoid_ingredients"],
            conditions=context["conditions"],
            max_time_min=context["max_time_min"],
            goal=context["goal"],
            limit=3,
        )
        candidates = self.rag.search(search_request)
        selected_recipes = [candidate.recipe for candidate in candidates]
        inventory_items = [
            InventoryItem(name=name, amount_g=999, location="message")
            for name in context["ingredients"]
        ]
        shopping_list = self.inventory.missing_for_recipes(selected_recipes, inventory_items)
        nutrition_summary = self.nutrition.sum_nutrition([candidate.nutrition for candidate in candidates])
        warnings = self._collect_warnings(context, candidates)
        answer = self._build_answer(candidates, shopping_list, nutrition_summary, warnings)

        return ChatResponse(
            answer=answer,
            recipes=candidates,
            shopping_list=shopping_list,
            nutrition_summary=nutrition_summary,
            warnings=warnings,
            parsed_context=context,
        )

    def _parse_message(self, user_id: str, message: str) -> dict:
        known_names = {item["name"] for item in self.ingredients.values()}
        ingredients = sorted(name for name in known_names if name in message)

        avoid_ingredients: list[str] = []
        for match in re.finditer(r"(?:不吃|不要|忌口|过敏)([^。；;，,\n]{0,12})", message):
            segment = match.group(1)
            for name in known_names:
                if name in segment:
                    avoid_ingredients.append(name)
        for name in known_names:
            if re.search(rf"{name}(?:过敏|不吃|不要|忌口)", message):
                avoid_ingredients.append(name)

        conditions: list[str] = []
        if "高血压" in message or "血压高" in message:
            conditions.append("hypertension")
        if "糖尿病" in message or "控糖" in message:
            conditions.append("diabetes")
        if "肾病" in message:
            conditions.append("kidney_disease")
        if "老人" in message or "我爸" in message or "我妈" in message:
            conditions.append("elderly")

        goal = None
        if "增肌" in message:
            goal = "bulking"
        elif "减脂" in message or "减肥" in message:
            goal = "cutting"
        elif "维持" in message:
            goal = "maintaining"

        time_match = re.search(r"(\d+)\s*分钟", message)
        max_time_min = int(time_match.group(1)) if time_match else None

        energy_match = re.search(r"消耗\s*(\d+)\s*(?:kcal|千卡|大卡)?", message, re.IGNORECASE)
        workout_energy_kcal = int(energy_match.group(1)) if energy_match else None

        return {
            "user_id": user_id,
            "ingredients": [item for item in ingredients if item not in avoid_ingredients],
            "avoid_ingredients": sorted(set(avoid_ingredients)),
            "conditions": sorted(set(conditions)),
            "goal": goal,
            "max_time_min": max_time_min,
            "workout_energy_kcal": workout_energy_kcal,
        }

    def _collect_warnings(self, context: dict, candidates) -> list[str]:
        warnings: list[str] = []
        warnings.extend(self.safety.summarize_conditions(context["conditions"]))
        for candidate in candidates:
            warnings.extend(candidate.warnings)
        if context["goal"] == "bulking":
            warnings.append("增肌期建议保证优质蛋白，并搭配适量主食帮助训练恢复。")
        if context["goal"] == "cutting":
            warnings.append("减脂期建议维持温和热量缺口，不建议过度节食。")
        return list(dict.fromkeys(warnings))

    def _build_answer(
        self,
        candidates,
        shopping_list: list[IngredientAmount],
        nutrition: NutritionFacts,
        warnings: list[str],
    ) -> str:
        if not candidates:
            return "没有找到完全匹配的菜谱。可以放宽做饭时间、减少限制，或补充更多可用食材。"

        lines: list[str] = []
        lines.append("根据你的食材、训练目标和健康约束，推荐下面这些菜：")
        for index, candidate in enumerate(candidates, start=1):
            recipe = candidate.recipe
            matched = "、".join(candidate.matched_ingredients) or "暂无"
            missing = "、".join(item.name for item in candidate.missing_ingredients) or "无需额外购买"
            lines.append(
                f"{index}. {recipe.name}：{recipe.cooking_time_min} 分钟，"
                f"约 {candidate.nutrition.calories} kcal，蛋白质 {candidate.nutrition.protein_g}g。"
                f"已有食材：{matched}；缺少：{missing}。"
            )

        if shopping_list:
            lines.append("购物清单：" + "、".join(f"{item.name} {item.amount_g:g}g" for item in shopping_list))
        else:
            lines.append("购物清单：当前食材基本够用。")

        lines.append(
            f"推荐菜合计约 {nutrition.calories} kcal，蛋白质 {nutrition.protein_g}g，"
            f"碳水 {nutrition.carbs_g}g，脂肪 {nutrition.fat_g}g，钠 {nutrition.sodium_mg}mg。"
        )

        if warnings:
            lines.append("注意：" + "；".join(warnings[:4]))

        return "\n".join(lines)
