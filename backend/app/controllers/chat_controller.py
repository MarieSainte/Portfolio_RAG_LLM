from fastapi import APIRouter, HTTPException
from app.schemas.chat_schema import ChatRequest, ChatResponse, HealthStatus
from app.services.mistral_service import mistral_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    reply = mistral_service.get_chat_response(request.message)
    if reply.startswith("Error:"):
        raise HTTPException(status_code=500, detail=reply)
    if reply == "Mistral API Key not configured on backend.":
        raise HTTPException(status_code=500, detail=reply)
    return ChatResponse(reply=reply)

@router.get("/health", response_model=HealthStatus)
async def health():
    return HealthStatus(status="ok")
