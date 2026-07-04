from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, health, inventory, meal_plans, nutrition, recipes, reminders, shopping
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "ok",
        "docs": "/docs",
    }


app.include_router(chat.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(nutrition.router, prefix="/api")
app.include_router(reminders.router, prefix="/api")
app.include_router(shopping.router, prefix="/api")
app.include_router(meal_plans.router, prefix="/api")
app.include_router(health.router, prefix="/api")

