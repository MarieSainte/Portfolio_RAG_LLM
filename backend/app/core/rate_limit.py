from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def _client_ip(request: Request) -> str:
    """Vraie IP du client : derrière le proxy nginx elle est dans X-Forwarded-For.

    Le backend n'est joignable que via le proxy (pas de port exposé sur l'hôte),
    donc on peut faire confiance à cet en-tête.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=_client_ip)
