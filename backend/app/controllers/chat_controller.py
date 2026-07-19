from fastapi import APIRouter, HTTPException, Request
from app.schemas.chat_schema import ChatRequest, ChatResponse, HealthStatus
from app.services.mistral_service import mistral_service
from app.core.config import settings
from app.core.rate_limit import limiter

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.CHAT_RATE_LIMIT)
async def chat(request: Request, payload: ChatRequest):
    history = [m.model_dump() for m in payload.history]
    reply = mistral_service.get_chat_response(payload.message, history)
    if reply.startswith("Error:"):
        raise HTTPException(status_code=500, detail=reply)
    if reply == "Mistral API Key not configured on backend.":
        raise HTTPException(status_code=500, detail=reply)
    return ChatResponse(reply=reply)

@router.get("/health", response_model=HealthStatus)
async def health():
    return HealthStatus(status="ok")
