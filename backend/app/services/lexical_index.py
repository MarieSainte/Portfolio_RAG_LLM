"""Index lexical BM25 via SQLite FTS5 — complément du dense retrieval (recherche hybride).

Le dense retrieval (embeddings) capte la proximité sémantique mais rate parfois
les correspondances exactes de mots-clés (noms de techno, acronymes : « FTS5 »,
« QLoRA », « Milvus »...). FTS5 apporte cette recherche lexicale exacte ; les
candidats des deux sources sont ensuite fusionnés puis reclassés par le
cross-encoder (voir rag_service.py).

L'index est reconstruit à chaque démarrage à partir des mêmes chunks que Chroma.
Le corpus (quelques projets) est petit, donc pas de persistance nécessaire : une
base SQLite en mémoire suffit et reste toujours cohérente avec le dense index.
"""

import logging
import re
import sqlite3
import threading

from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Colonnes indexées (searchable) vs UNINDEXED (stockées, non tokenisées).
# remove_diacritics 2 : « échecs » matche « echecs » (requête et contenu normalisés).
_CREATE_SQL = """
DROP TABLE IF EXISTS chunks;
CREATE VIRTUAL TABLE chunks USING fts5(
    content,
    doc_id UNINDEXED,
    project_id UNINDEXED,
    link UNINDEXED,
    type UNINDEXED,
    chunk_index UNINDEXED,
    tokenize = 'unicode61 remove_diacritics 2'
);
"""


def _to_fts_match(query: str) -> str:
    """Transforme une requête utilisateur en expression MATCH FTS5 sûre.

    Chaque mot est isolé et mis entre guillemets (traité comme littéral), ce qui
    neutralise les opérateurs FTS5 (AND, OR, NEAR, *, -, ...) présents dans le
    texte libre et évite les erreurs de syntaxe / injections. Les tokens sont
    joints par OR pour maximiser le rappel : le reranking tranche ensuite.
    """
    tokens = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 1]
    return " OR ".join(f'"{t}"' for t in tokens)


class LexicalIndex:
    """Recherche lexicale BM25 sur les chunks, adossée à SQLite FTS5.

    Dégradation gracieuse : si FTS5 n'est pas compilé dans le SQLite embarqué,
    l'index se désactive (search renvoie []) et le pipeline retombe sur le seul
    dense retrieval.
    """

    def __init__(self):
        self._conn = None
        self._lock = threading.Lock()

    @property
    def available(self) -> bool:
        return self._conn is not None

    def build(self, records: list[dict]) -> None:
        """(Re)construit l'index. records : dicts {doc_id, content, project_id, link, type, chunk_index}."""
        try:
            conn = sqlite3.connect(":memory:", check_same_thread=False)
            conn.executescript(_CREATE_SQL)
        except sqlite3.OperationalError:
            logger.warning("FTS5 indisponible dans SQLite — recherche lexicale désactivée")
            self._conn = None
            return

        with self._lock:
            conn.executemany(
                "INSERT INTO chunks (content, doc_id, project_id, link, type, chunk_index) "
                "VALUES (:content, :doc_id, :project_id, :link, :type, :chunk_index)",
                records,
            )
            conn.commit()
            self._conn = conn
        logger.info("index lexical FTS5 construit", extra={"context": {"chunks": len(records)}})

    def search(self, query: str, k: int) -> list[Document]:
        """Renvoie jusqu'à k chunks classés par pertinence BM25 (meilleurs d'abord)."""
        if self._conn is None:
            return []
        match = _to_fts_match(query)
        if not match:
            return []
        try:
            with self._lock:
                rows = self._conn.execute(
                    "SELECT content, project_id, link, type, chunk_index FROM chunks "
                    "WHERE chunks MATCH ? ORDER BY bm25(chunks) LIMIT ?",
                    (match, k),
                ).fetchall()
        except sqlite3.OperationalError:
            logger.exception("erreur requête FTS5")
            return []
        return [
            Document(
                page_content=content,
                metadata={
                    "project_id": project_id,
                    "link": link,
                    "type": doc_type,
                    "chunk_index": chunk_index,
                },
            )
            for content, project_id, link, doc_type, chunk_index in rows
        ]
