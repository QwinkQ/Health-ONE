from fastapi import APIRouter, HTTPException

from app.core.schemas import Recipe, RecipeCandidate, RecipeSearchRequest
from app.services.data_store import find_recipe, get_recipes
from app.services.rag_service import RagService

router = APIRouter(prefix="/recipes", tags=["recipes"])
rag = RagService()


@router.get("", response_model=list[Recipe])
def list_recipes() -> list[Recipe]:
    return get_recipes()


@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: str) -> Recipe:
    recipe = find_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/search", response_model=list[RecipeCandidate])
def search_recipes(request: RecipeSearchRequest) -> list[RecipeCandidate]:
    return rag.search(request)

