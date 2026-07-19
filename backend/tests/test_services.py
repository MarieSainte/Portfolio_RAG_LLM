from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage

from app.services.mistral_service import (
    MAX_HISTORY_MESSAGES,
    _format_docs,
    _to_lc_messages,
)


def test_format_docs_empty():
    assert "Aucune information" in _format_docs([])


def test_format_docs_with_link():
    docs = [Document(page_content="Projet X", metadata={"link": "https://gh/x"})]
    out = _format_docs(docs)
    assert "Projet X" in out
    assert "https://gh/x" in out


def test_format_docs_ignores_nan_link():
    docs = [Document(page_content="Projet Y", metadata={"link": "nan"})]
    out = _format_docs(docs)
    assert "Projet Y" in out
    assert "Lien" not in out


def test_to_lc_messages_roles():
    history = [
        {"role": "user", "content": "salut"},
        {"role": "assistant", "content": "bonjour"},
    ]
    msgs = _to_lc_messages(history)
    assert isinstance(msgs[0], HumanMessage)
    assert isinstance(msgs[1], AIMessage)


def test_to_lc_messages_caps_length():
    history = [{"role": "user", "content": str(i)} for i in range(50)]
    msgs = _to_lc_messages(history)
    assert len(msgs) == MAX_HISTORY_MESSAGES
    # On garde bien les plus récents
    assert msgs[-1].content == "49"


def test_to_lc_messages_empty():
    assert _to_lc_messages(None) == []
    assert _to_lc_messages([]) == []
