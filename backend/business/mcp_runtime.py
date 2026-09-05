from __future__ import annotations

from typing import Any, Dict
import os

from backend.data_access.config import SQLAnywhereSettings
import sys

from backend.mcp_core.mcp.client import MCPClient
from backend.mcp_core.mcp.stdio_client import StdioTransport
from backend.mcp_core.mcp.http_transport import HTTPTransport


_active_transports: list[StdioTransport] = []


def create_business_mcp_client(settings: SQLAnywhereSettings) -> tuple[MCPClient, list[dict[str, Any]]]:
    """Create a local or remote MCP client based on MCP_TRANSPORT."""
    if os.getenv("MCP_TRANSPORT", "stdio").lower() == "http":
        url = os.getenv("MCP_REMOTE_URL", "http://127.0.0.1:8080/mcp")
        transport = HTTPTransport(url, token=os.getenv("MCP_REMOTE_TOKEN", ""), timeout=60)
        client = MCPClient(transport)
        client.initialize()
        return client, client.list_tools()["tools"]
    transport = StdioTransport([sys.executable, "-m", "backend.business.server"], timeout=60)
    transport.start()
    _active_transports.append(transport)
    client = MCPClient(transport)
    client.initialize()
    definitions = client.list_tools()["tools"]
    return client, definitions
