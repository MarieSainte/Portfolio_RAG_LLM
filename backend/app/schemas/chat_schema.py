from typing import Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    # Historique de la conversation (multi-tours), le plus ancien en premier
    history: list[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str


class HealthStatus(BaseModel):
    status: str
