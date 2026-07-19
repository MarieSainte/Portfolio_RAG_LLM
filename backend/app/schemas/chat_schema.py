from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    # Bornes anti-abus : protègent la latence et les coûts de tokens
    message: str = Field(min_length=1, max_length=2000)
    # Historique de la conversation (multi-tours), le plus ancien en premier
    history: list[Message] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    reply: str


class HealthStatus(BaseModel):
    status: str
