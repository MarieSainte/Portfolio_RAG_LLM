import pytest
from pydantic import ValidationError

from app.schemas.chat_schema import ChatRequest, Message


def test_chat_request_defaults_empty_history():
    req = ChatRequest(message="Bonjour")
    assert req.message == "Bonjour"
    assert req.history == []


def test_chat_request_parses_history():
    req = ChatRequest(
        message="Et ensuite ?",
        history=[
            {"role": "user", "content": "Parle-moi du projet X"},
            {"role": "assistant", "content": "Le projet X utilise..."},
        ],
    )
    assert len(req.history) == 2
    assert isinstance(req.history[0], Message)
    assert req.history[1].role == "assistant"


def test_chat_request_rejects_invalid_role():
    with pytest.raises(ValidationError):
        ChatRequest(message="x", history=[{"role": "system", "content": "nope"}])


def test_chat_request_requires_message():
    with pytest.raises(ValidationError):
        ChatRequest(history=[])
