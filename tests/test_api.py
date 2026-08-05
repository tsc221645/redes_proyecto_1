import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.api.app import app, session_manager
from backend.llm.sessions import SessionManager


class FakeChat:
    def __init__(self):
        self.last_conversation = []

    def run(self, messages):
        self.last_conversation = list(messages)
        return "respuesta de prueba"


def test_health():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}


def test_create_get_and_delete_session():
    original = app_module_manager = session_manager
    import backend.api.app as api_module
    api_module.session_manager = SessionManager(FakeChat)
    try:
        client = TestClient(app)
        created = client.post("/api/chat/sessions")
        assert created.status_code == 201
        session_id = created.json()["session_id"]
        message = client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": "Hola"})
        assert message.json()["response"] == "respuesta de prueba"
        assert client.get(f"/api/chat/sessions/{session_id}").status_code == 200
        assert client.delete(f"/api/chat/sessions/{session_id}").status_code == 204
    finally:
        api_module.session_manager = original
