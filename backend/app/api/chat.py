from fastapi import APIRouter

from app.core.schemas import ChatRequest, ChatResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/chat", tags=["chat"])
agent = AgentService()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return agent.handle_chat(request.user_id, request.message)

