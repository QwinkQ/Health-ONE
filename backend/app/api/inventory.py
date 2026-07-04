from fastapi import APIRouter

from app.core.schemas import InventoryItem, InventoryUpsertRequest

router = APIRouter(prefix="/inventory", tags=["inventory"])
_inventory_by_user: dict[str, list[InventoryItem]] = {
    "demo-user": [
        InventoryItem(name="鸡胸肉", amount_g=300, location="fridge"),
        InventoryItem(name="番茄", amount_g=300, location="fridge"),
        InventoryItem(name="鸡蛋", amount_g=150, location="fridge"),
        InventoryItem(name="菠菜", amount_g=200, location="fridge"),
    ]
}


@router.get("/{user_id}", response_model=list[InventoryItem])
def get_inventory(user_id: str) -> list[InventoryItem]:
    return _inventory_by_user.get(user_id, [])


@router.post("/{user_id}", response_model=list[InventoryItem])
def upsert_inventory(user_id: str, request: InventoryUpsertRequest) -> list[InventoryItem]:
    _inventory_by_user[user_id] = request.items
    return _inventory_by_user[user_id]

