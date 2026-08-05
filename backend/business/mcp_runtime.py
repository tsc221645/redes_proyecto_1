from __future__ import annotations

from typing import Any, Dict

from backend.data_access.config import SQLAnywhereSettings
from backend.mcp_core.mcp.client import MCPClient
from backend.mcp_core.mcp.server import MCPServer
from backend.mcp_core.mcp.types import ServerInfo
from .mcp_tools import create_business_mcp_tools
from .registry import BusinessToolRegistry


class InProcessMCPTransport:
    """In-process transport used by the local chatbot during Phase 7."""

    def __init__(self, server: MCPServer) -> None:
        self.server = server

    def send(self, message: Dict[str, Any]) -> Dict[str, Any] | None:
        return self.server.handle(message)


def create_business_mcp_client(settings: SQLAnywhereSettings) -> tuple[MCPClient, list[dict[str, Any]]]:
    """Create a local MCP client and expose its tools to the LLM."""
    tools = BusinessToolRegistry(create_business_mcp_tools(settings)).all()
    server = MCPServer(ServerInfo("business-mcp-server", "0.1.0"), tools)
    client = MCPClient(InProcessMCPTransport(server))
    client.initialize()
    definitions = client.list_tools()["tools"]
    return client, definitions
