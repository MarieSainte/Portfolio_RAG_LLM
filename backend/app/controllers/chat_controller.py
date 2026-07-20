import logging
import time

from fastapi import APIRouter, Header, HTTPException, Query, Request

from app.core.config import settings
from app.core.rate_limit import limiter
from app.schemas.chat_schema import ChatRequest, ChatResponse, HealthStatus, InteractionOut
from app.services.interaction_store import interaction_store
from app.services.mistral_service import mistral_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.CHAT_RATE_LIMIT)
async def chat(request: Request, payload: ChatRequest):
    history = [m.model_dump() for m in payload.history]
    start = time.perf_counter()
    reply, contexts = mistral_service.answer_with_contexts(payload.message, history)
    latency_ms = int((time.perf_counter() - start) * 1000)

    # On ne renvoie jamais le détail interne d'une erreur au client (pas de fuite)
    if reply.startswith("Error:") or reply == "Mistral API Key not configured on backend.":
        logger.error("chat request failed", extra={"context": {"reason": reply}})
        raise HTTPException(
            status_code=500,
            detail="Une erreur est survenue lors de la génération de la réponse.",
        )

    # Latence exposée aux logs structurés -> Loki -> panel Grafana.
    logger.info(
        "chat request completed",
        extra={"context": {"latency_ms": latency_ms, "session_id": payload.session_id}},
    )

    # Journalisation de l'échange (résiliente : n'interrompt jamais la réponse).
    interaction_store.record(
        question=payload.message,
        answer=reply,
        contexts=contexts,
        session_id=payload.session_id,
        latency_ms=latency_ms,
    )
    return ChatResponse(reply=reply)


@router.get("/health", response_model=HealthStatus)
async def health():
    return HealthStatus(status="ok")


def _require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    """Protège les endpoints d'administration.

    Endpoint désactivé (404) tant qu'ADMIN_TOKEN n'est pas configuré : le journal
    d'interactions n'est jamais exposé publiquement par défaut.
    """
    if not settings.ADMIN_TOKEN:
        raise HTTPException(status_code=404, detail="Not Found")
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/admin/interactions", response_model=list[InteractionOut])
async def list_interactions(
    q: str | None = Query(
        default=None, description="Recherche plein-texte (FTS5) ; vide = plus récentes"
    ),
    limit: int = Query(default=20, ge=1, le=200),
    x_admin_token: str | None = Header(default=None),
):
    """Consulte le journal des interactions : recherche FTS5 si `q`, sinon les plus récentes."""
    _require_admin(x_admin_token)
    if q:
        return interaction_store.search(q, limit)
    return interaction_store.recent(limit)
