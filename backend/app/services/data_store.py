from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.schemas import Recipe

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _read_json(name: str) -> Any:
    with (DATA_DIR / name).open("r", encoding="utf-8") as file:
        return json.load(file)


@lru_cache
def get_recipes() -> list[Recipe]:
    return [Recipe.model_validate(item) for item in _read_json("seed_recipes.json")]


@lru_cache
def get_ingredients() -> dict[str, dict[str, Any]]:
    ingredients = {}
    for item in _read_json("seed_ingredients.json"):
        ingredients[item["name"]] = item
        for alias in item.get("aliases", []):
            ingredients[alias] = item
    return ingredients


@lru_cache
def get_safety_rules() -> dict[str, Any]:
    return _read_json("safety_rules.json")


def find_recipe(recipe_id: str) -> Recipe | None:
    return next((recipe for recipe in get_recipes() if recipe.id == recipe_id), None)

