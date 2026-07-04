from fastapi import APIRouter, HTTPException

from app.core.schemas import NutritionCalculateRequest, NutritionFacts
from app.services.data_store import find_recipe
from app.services.nutrition_service import NutritionService

router = APIRouter(prefix="/nutrition", tags=["nutrition"])
nutrition = NutritionService()


@router.post("/calculate", response_model=NutritionFacts)
def calculate_nutrition(request: NutritionCalculateRequest) -> NutritionFacts:
    recipe = find_recipe(request.recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return nutrition.calculate_recipe(recipe, servings=request.servings)

