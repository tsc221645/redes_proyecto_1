from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4

from .orchestrator import ChatOrchestrator


@dataclass
class ChatSession:
    session_id: str
    orchestrator: ChatOrchestrator
    max_messages: int = 20
    messages: List[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def send(self, content: str) -> str:
        self.messages.append({"role": "user", "content": content})
        response = self.orchestrator.run(self.messages)
        self.messages = self.orchestrator.last_conversation[-self.max_messages:]
        self.messages.append({"role": "assistant", "content": response})
        self.messages = self.messages[-self.max_messages:]
        return response

    def clear(self) -> None:
        self.messages.clear()

    @property
    def last_tool_results(self) -> List[dict]:
        return getattr(self.orchestrator, "last_tool_results", [])


class SessionManager:
    """In-memory session store for the local academic prototype."""

    def __init__(self, factory, *, max_messages: int = 20) -> None:
        self.factory = factory
        self.max_messages = max_messages
        self._sessions: Dict[str, ChatSession] = {}

    def create(self) -> ChatSession:
        session = ChatSession(uuid4().hex, self.factory(), self.max_messages)
        session.messages.append({"role": "system", "content": "Answer in Spanish. Use MCP tool results for business facts. Distinguish data from hypotheses and state when evidence is insufficient."})
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> ChatSession:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError(f"Unknown session: {session_id}") from exc

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def clear(self, session_id: str) -> None:
        self.get(session_id).clear()
