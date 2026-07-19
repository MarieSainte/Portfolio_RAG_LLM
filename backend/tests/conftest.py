import os

# Doit être défini AVANT l'import de l'app (lu à la construction des settings / routes).
os.environ.setdefault("MISTRAL_API_KEY", "test-key")
os.environ.setdefault("CHAT_RATE_LIMIT", "10/minute")

import pytest
from fastapi.testclient import TestClient

from app.core.rate_limit import limiter
from app.main import app


@pytest.fixture
def client():
    """Client de test SANS lifespan (pas d'indexation ni de chargement de modèles ML).

    On instancie TestClient sans le context manager : les hooks startup/shutdown
    ne sont pas déclenchés, ce qui garde les tests rapides et hors-réseau.
    Le rate-limiter est désactivé par défaut (réactivé dans le test dédié).
    """
    limiter.enabled = False
    yield TestClient(app)
    limiter.enabled = True
