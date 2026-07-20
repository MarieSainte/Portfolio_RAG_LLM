"""Journalisation persistante des interactions chat dans SQLite, recherchable via FTS5.

Chaque échange (question / réponse / contextes / latence) est enregistré dans une
table `interactions`. Un index FTS5 *external-content* (`interactions_fts`) miroite
les colonnes texte et reste synchronisé par triggers, ce qui permet une recherche
plein-texte BM25 sur l'historique (« qu'est-ce que les recruteurs demandent ? »).

Contrairement à l'index lexical du RAG (en mémoire, reconstruit au démarrage), ce
store est **persistant** : la base vit dans un fichier (voir INTERACTIONS_DB_PATH).
La journalisation ne doit jamais casser la requête chat -> record() avale ses erreurs.
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.services.lexical_index import _to_fts_match

logger = logging.getLogger(__name__)

# Table de données + index FTS5 external-content synchronisé par triggers (pattern SQLite
# canonique : on n'écrit que dans `interactions`, les triggers maintiennent l'index).
_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    session_id TEXT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    contexts TEXT,
    latency_ms INTEGER
);
CREATE VIRTUAL TABLE IF NOT EXISTS interactions_fts USING fts5(
    question, answer,
    content='interactions', content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER IF NOT EXISTS interactions_ai AFTER INSERT ON interactions BEGIN
    INSERT INTO interactions_fts(rowid, question, answer)
    VALUES (new.id, new.question, new.answer);
END;
CREATE TRIGGER IF NOT EXISTS interactions_ad AFTER DELETE ON interactions BEGIN
    INSERT INTO interactions_fts(interactions_fts, rowid, question, answer)
    VALUES ('delete', old.id, old.question, old.answer);
END;
CREATE TRIGGER IF NOT EXISTS interactions_au AFTER UPDATE ON interactions BEGIN
    INSERT INTO interactions_fts(interactions_fts, rowid, question, answer)
    VALUES ('delete', old.id, old.question, old.answer);
    INSERT INTO interactions_fts(rowid, question, answer)
    VALUES (new.id, new.question, new.answer);
END;
"""

# Colonnes qualifiées (i.) : la recherche joint interactions_fts, qui expose aussi
# des colonnes question/answer -> évite l'erreur "ambiguous column name".
_SELECT_COLS = "i.id, i.created_at, i.session_id, i.question, i.answer, i.contexts, i.latency_ms"


def _row_to_dict(row: tuple) -> dict:
    id_, created_at, session_id, question, answer, contexts, latency_ms = row
    return {
        "id": id_,
        "created_at": created_at,
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "contexts": json.loads(contexts) if contexts else [],
        "latency_ms": latency_ms,
    }


class InteractionStore:
    """Persiste et interroge l'historique des interactions chat (SQLite + FTS5)."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._conn = None
        self._lock = threading.Lock()

    @property
    def available(self) -> bool:
        return self._conn is not None

    def connect(self) -> None:
        """Ouvre la base et crée le schéma (idempotent). À appeler au démarrage."""
        try:
            if self._db_path != ":memory:":
                Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self._db_path, check_same_thread=False)
            # WAL : lectures concurrentes pendant les écritures (l'admin lit, /chat écrit).
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(_SCHEMA_SQL)
            conn.commit()
        except sqlite3.OperationalError:
            logger.exception(
                "interaction store: échec d'initialisation — journalisation désactivée"
            )
            self._conn = None
            return
        with self._lock:
            self._conn = conn
        logger.info("interaction store prêt", extra={"context": {"path": self._db_path}})

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def record(
        self,
        question: str,
        answer: str,
        contexts: list[str] | None = None,
        session_id: str | None = None,
        latency_ms: int | None = None,
    ) -> None:
        """Enregistre une interaction. Résilient : n'interrompt jamais la requête chat."""
        if self._conn is None:
            return
        try:
            with self._lock:
                self._conn.execute(
                    "INSERT INTO interactions "
                    "(created_at, session_id, question, answer, contexts, latency_ms) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        datetime.now(timezone.utc).isoformat(),
                        session_id,
                        question,
                        answer,
                        json.dumps(contexts or [], ensure_ascii=False),
                        latency_ms,
                    ),
                )
                self._conn.commit()
        except sqlite3.Error:
            logger.exception("interaction store: échec d'enregistrement")

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """Recherche plein-texte BM25 sur question + réponse (meilleurs d'abord)."""
        if self._conn is None:
            return []
        match = _to_fts_match(query)
        if not match:
            return []
        try:
            with self._lock:
                rows = self._conn.execute(
                    f"SELECT {_SELECT_COLS} FROM interactions_fts f "
                    "JOIN interactions i ON i.id = f.rowid "
                    "WHERE interactions_fts MATCH ? ORDER BY bm25(interactions_fts) LIMIT ?",
                    (match, limit),
                ).fetchall()
        except sqlite3.OperationalError:
            logger.exception("interaction store: erreur de recherche FTS5")
            return []
        return [_row_to_dict(r) for r in rows]

    def recent(self, limit: int = 20) -> list[dict]:
        """Renvoie les interactions les plus récentes (plus récentes d'abord)."""
        if self._conn is None:
            return []
        with self._lock:
            rows = self._conn.execute(
                f"SELECT {_SELECT_COLS} FROM interactions i ORDER BY i.id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [_row_to_dict(r) for r in rows]


# Singleton (connexion ouverte au démarrage via lifespan).
interaction_store = InteractionStore(settings.INTERACTIONS_DB_PATH)
