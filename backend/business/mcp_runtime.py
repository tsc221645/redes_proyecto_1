from __future__ import annotations

from typing import Any, Dict

from backend.data_access.config import SQLAnywhereSettings
import sys

from backend.mcp_core.mcp.client import MCPClient
from backend.mcp_core.mcp.stdio_client import StdioTransport


_active_transports: list[StdioTransport] = []


def create_business_mcp_client(settings: SQLAnywhereSettings) -> tuple[MCPClient, list[dict[str, Any]]]:
    """Create a local MCP client and expose its tools to the LLM."""
    transport = StdioTransport([sys.executable, "-m", "backend.business.server"], timeout=60)
    transport.start()
    _active_transports.append(transport)
    client = MCPClient(transport)
    client.initialize()
    definitions = client.list_tools()["tools"]
    return client, definitions
