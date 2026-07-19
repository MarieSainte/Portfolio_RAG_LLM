import logging

from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.core.rate_limit import limiter
from app.schemas.chat_schema import ChatRequest, ChatResponse, HealthStatus
from app.services.mistral_service import mistral_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.CHAT_RATE_LIMIT)
async def chat(request: Request, payload: ChatRequest):
    history = [m.model_dump() for m in payload.history]
    reply = mistral_service.get_chat_response(payload.message, history)

    # On ne renvoie jamais le détail interne d'une erreur au client (pas de fuite)
    if reply.startswith("Error:") or reply == "Mistral API Key not configured on backend.":
        logger.error("chat request failed", extra={"context": {"reason": reply}})
        raise HTTPException(
            status_code=500,
            detail="Une erreur est survenue lors de la génération de la réponse.",
        )
    return ChatResponse(reply=reply)


@router.get("/health", response_model=HealthStatus)
async def health():
    return HealthStatus(status="ok")
