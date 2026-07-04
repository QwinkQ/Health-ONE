from fastapi import APIRouter

from app.core.schemas import ChatRequest, ChatResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/meal-plans", tags=["meal-plans"])
agent = AgentService()


@router.post("/generate", response_model=ChatResponse)
def generate_meal_plan(request: ChatRequest) -> ChatResponse:
    return agent.handle_chat(request.user_id, request.message)

