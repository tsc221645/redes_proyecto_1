from __future__ import annotations

from typing import Any, Dict, List

from backend.business.mcp_runtime import create_business_mcp_client
from backend.data_access.config import SQLAnywhereSettings
from .orchestrator import ChatOrchestrator
from .provider import LiteLLMProvider, tool_schema


def create_business_chat() -> ChatOrchestrator:
    """Build the Phase 7 local chatbot using LiteLLM and the MCP client."""
    settings = SQLAnywhereSettings.from_env()
    mcp_client, definitions = create_business_mcp_client(settings)
    schemas = [tool_schema(item["name"], item["description"], item["inputSchema"]) for item in definitions]
    handlers = {
        item["name"]: (lambda arguments, name=item["name"]: mcp_client.call_tool(name, arguments))
        for item in definitions
    }
    return ChatOrchestrator(LiteLLMProvider.from_env(), handlers, tool_schemas=schemas)


def ask(question: str) -> str:
    """Ask one question using a fresh local MCP-backed conversation."""
    chatbot = create_business_chat()
    return chatbot.run([
        {"role": "system", "content": "Answer in Spanish. Use only tool results for business facts. State when evidence is insufficient."},
        {"role": "user", "content": question},
    ])
