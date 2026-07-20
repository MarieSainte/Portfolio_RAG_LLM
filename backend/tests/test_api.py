import app.controllers.chat_controller as controller
from app.core.rate_limit import limiter


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_chat_ok(client, monkeypatch):
    captured = {}

    def fake_response(message, history=None):
        captured["message"] = message
        captured["history"] = history
        return "Réponse de test", ["contexte"]

    monkeypatch.setattr(controller.mistral_service, "answer_with_contexts", fake_response)

    resp = client.post(
        "/chat",
        json={
            "message": "Parle-moi de Jordan",
            "history": [{"role": "user", "content": "salut"}],
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"reply": "Réponse de test"}
    # Le contrôleur transmet bien le message et l'historique au service
    assert captured["message"] == "Parle-moi de Jordan"
    assert captured["history"] == [{"role": "user", "content": "salut"}]


def test_chat_service_error_returns_500(client, monkeypatch):
    monkeypatch.setattr(
        controller.mistral_service,
        "answer_with_contexts",
        lambda message, history=None: ("Error: boom", []),
    )
    resp = client.post("/chat", json={"message": "x"})
    assert resp.status_code == 500


def test_chat_missing_message_returns_422(client):
    resp = client.post("/chat", json={"history": []})
    assert resp.status_code == 422


def test_chat_rate_limited(client, monkeypatch):
    # Réponse instantanée pour ne pas dépendre du LLM
    monkeypatch.setattr(
        controller.mistral_service,
        "answer_with_contexts",
        lambda message, history=None: ("ok", []),
    )
    # Le limiteur est désactivé par les autres tests, son compteur est donc à zéro ici.
    limiter.enabled = True

    statuses = [client.post("/chat", json={"message": "x"}).status_code for _ in range(12)]
    assert 429 in statuses
    # Les premières requêtes passent avant que la limite (10/minute) ne coupe
    assert statuses[0] == 200
