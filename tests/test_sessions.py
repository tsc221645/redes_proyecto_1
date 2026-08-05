import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.llm.sessions import SessionManager


class FakeChat:
    def __init__(self):
        self.last_conversation = []

    def run(self, messages):
        self.last_conversation = list(messages)
        return f"answer {len(messages)}"


def test_session_keeps_context_and_can_clear():
    manager = SessionManager(FakeChat, max_messages=5)
    session = manager.create()
    session.send("first question")
    session.send("follow-up question")
    assert any(message["content"] == "first question" for message in session.messages)
    session.clear()
    assert session.messages == []


def test_manager_rejects_unknown_session():
    manager = SessionManager(FakeChat)
    try:
        manager.get("missing")
        assert False
    except KeyError:
        assert True
