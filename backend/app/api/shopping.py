from fastapi import APIRouter, HTTPException

from app.core.schemas import IngredientAmount, ShoppingListRequest
from app.services.data_store import find_recipe
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/shopping-list", tags=["shopping-list"])
inventory_service = InventoryService()


@router.post("/generate", response_model=list[IngredientAmount])
def generate_shopping_list(request: ShoppingListRequest) -> list[IngredientAmount]:
    recipes = []
    for recipe_id in request.recipe_ids:
        recipe = find_recipe(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail=f"Recipe not found: {recipe_id}")
        recipes.append(recipe)
    return inventory_service.missing_for_recipes(recipes, request.inventory)

