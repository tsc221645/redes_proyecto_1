from __future__ import annotations

from .business_chat import create_business_chat
from .sessions import SessionManager


def create_session_manager() -> SessionManager:
    """Create the session service; each session gets its own MCP/LLM context."""
    return SessionManager(create_business_chat)
