import pytest

from app.core.config import settings
from app.services.interaction_store import InteractionStore, interaction_store


@pytest.fixture
def store(tmp_path):
    s = InteractionStore(str(tmp_path / "interactions.db"))
    s.connect()
    if not s.available:
        pytest.skip("FTS5 indisponible dans ce build SQLite")
    yield s
    s.close()


def test_record_and_recent(store):
    store.record(
        "Quelles technos ?", "Python et FastAPI.", contexts=["ctx1"], session_id="s1", latency_ms=42
    )
    rows = store.recent(10)
    assert len(rows) == 1
    r = rows[0]
    assert r["question"] == "Quelles technos ?"
    assert r["answer"] == "Python et FastAPI."
    assert r["contexts"] == ["ctx1"]
    assert r["session_id"] == "s1"
    assert r["latency_ms"] == 42
    assert r["created_at"]  # horodatage renseigné


def test_recent_orders_newest_first(store):
    store.record("q1", "a1")
    store.record("q2", "a2")
    assert [r["question"] for r in store.recent(10)] == ["q2", "q1"]


def test_search_fts_matches_question_and_answer(store):
    store.record("Parle-moi de Milvus", "C'est une base vectorielle.")
    store.record("Parle-moi de Docker", "Docker conteneurise les apps.")
    rows = store.search("Milvus", 10)
    assert len(rows) == 1
    assert "Milvus" in rows[0]["question"]
    # Le contenu de la réponse est aussi indexé.
    assert len(store.search("conteneurise", 10)) == 1


def test_search_no_match_returns_empty(store):
    store.record("q", "a")
    assert store.search("kubernetes", 10) == []


def test_search_empty_query_returns_empty(store):
    store.record("q", "a")
    assert store.search("  ?? ", 10) == []


def test_record_without_connect_is_noop(tmp_path):
    s = InteractionStore(str(tmp_path / "x.db"))  # pas de connect()
    s.record("q", "a")  # ne doit pas lever
    assert s.recent(10) == []


# --- Endpoint d'administration ---


def test_admin_disabled_returns_404(client):
    # ADMIN_TOKEN vaut None par défaut -> feature désactivée.
    assert client.get("/admin/interactions").status_code == 404


def test_admin_requires_valid_token(client, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_TOKEN", "secret")
    assert client.get("/admin/interactions").status_code == 403
    assert client.get("/admin/interactions", headers={"X-Admin-Token": "wrong"}).status_code == 403


def test_admin_lists_and_searches(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_TOKEN", "secret")
    monkeypatch.setattr(interaction_store, "_db_path", str(tmp_path / "i.db"))
    interaction_store._conn = None
    interaction_store.connect()
    if not interaction_store.available:
        pytest.skip("FTS5 indisponible dans ce build SQLite")
    try:
        interaction_store.record("Quelles technos ?", "Python et FastAPI.", contexts=["c"])
        headers = {"X-Admin-Token": "secret"}

        resp = client.get("/admin/interactions", headers=headers)
        assert resp.status_code == 200
        assert resp.json()[0]["question"] == "Quelles technos ?"

        resp = client.get("/admin/interactions", params={"q": "FastAPI"}, headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

        resp = client.get("/admin/interactions", params={"q": "kubernetes"}, headers=headers)
        assert resp.json() == []
    finally:
        interaction_store.close()
