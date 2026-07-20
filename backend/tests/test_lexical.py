import pytest

from app.services.lexical_index import LexicalIndex, _to_fts_match

RECORDS = [
    {
        "doc_id": "1_chunk_0",
        "content": "Fine-tuning de Qwen3 en QLoRA 4-bit avec Unsloth pour le triage médical.",
        "project_id": "1",
        "link": "https://gh/triage",
        "type": "Projet etudiant",
        "chunk_index": 0,
    },
    {
        "doc_id": "2_chunk_0",
        "content": "Agent d'échecs pour la FFE avec Milvus, LangGraph et Stockfish.",
        "project_id": "2",
        "link": "https://gh/ffe",
        "type": "Projet etudiant",
        "chunk_index": 0,
    },
]


def test_to_fts_match_quotes_and_ors_tokens():
    assert _to_fts_match("Milvus LangGraph") == '"milvus" OR "langgraph"'


def test_to_fts_match_drops_short_and_neutralizes_operators():
    # « OR », « a » (<=1 char) sont ignorés ; les opérateurs FTS5 deviennent des littéraux.
    assert _to_fts_match("a OR b") == '"or"'


def test_to_fts_match_empty_on_punctuation():
    assert _to_fts_match("?!  ...") == ""


@pytest.fixture
def index():
    idx = LexicalIndex()
    idx.build(RECORDS)
    if not idx.available:
        pytest.skip("FTS5 indisponible dans ce build SQLite")
    return idx


def test_search_finds_exact_keyword(index):
    docs = index.search("Milvus", k=5)
    assert len(docs) == 1
    assert docs[0].metadata["project_id"] == "2"
    assert docs[0].metadata["link"] == "https://gh/ffe"


def test_search_is_diacritics_insensitive(index):
    # « echecs » (sans accent) doit matcher « échecs » (remove_diacritics).
    docs = index.search("echecs", k=5)
    assert any(d.metadata["project_id"] == "2" for d in docs)


def test_search_no_match_returns_empty(index):
    assert index.search("kubernetes", k=5) == []


def test_search_empty_query_returns_empty(index):
    assert index.search("  ??  ", k=5) == []


def test_search_without_build_returns_empty():
    assert LexicalIndex().search("Milvus", k=5) == []
