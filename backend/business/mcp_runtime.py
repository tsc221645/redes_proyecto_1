from __future__ import annotations

from typing import Any, Dict
import os
import subprocess
from pathlib import Path

from backend.data_access.config import SQLAnywhereSettings
import sys

from backend.mcp_core.mcp.client import MCPClient
from backend.mcp_core.mcp.stdio_client import StdioTransport
from backend.mcp_core.mcp.http_transport import HTTPTransport
from backend.mcp_core.mcp.official_servers import filesystem_command, git_command


_active_transports: list[StdioTransport] = []


class MCPClientPool:
    """Present several MCP servers through the same tool-call interface."""

    def __init__(self, clients: dict[str, MCPClient], definitions: list[dict[str, Any]]) -> None:
        self.clients = clients
        self.definitions = definitions
        self._owners = {
            tool["name"]: server_name
            for server_name, client in clients.items()
            for tool in client.list_tools()["tools"]
        }

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        server_name = self._owners.get(name)
        if server_name is None:
            raise RuntimeError(f"Tool not found: {name}")
        return self.clients[server_name].call_tool(name, arguments)


def create_business_mcp_client(settings: SQLAnywhereSettings) -> tuple[MCPClient | MCPClientPool, list[dict[str, Any]]]:
    """Create a local or remote MCP client based on MCP_TRANSPORT."""
    if os.getenv("MCP_TRANSPORT", "stdio").lower() == "http":
        url = os.getenv("MCP_REMOTE_URL", "http://127.0.0.1:8080/mcp")
        transport = HTTPTransport(url, token=os.getenv("MCP_REMOTE_TOKEN", ""), timeout=60)
        client = MCPClient(transport, server_name="business-mcp-remote")
        client.initialize()
        return client, client.list_tools()["tools"]
    transport = StdioTransport([sys.executable, "-m", "backend.business.server"], timeout=60)
    transport.start()
    _active_transports.append(transport)
    client = MCPClient(transport, server_name="business-mcp-server")
    client.initialize()
    definitions = client.list_tools()["tools"]
    clients = {"business": client}
    enabled = [item.strip().lower() for item in os.getenv("MCP_OFFICIAL_SERVERS", "").split(",") if item.strip()]
    if enabled:
        root = Path(os.getenv("MCP_OFFICIAL_WORKSPACE", "phase4_demo")).resolve()
        root.mkdir(parents=True, exist_ok=True)
        if "git" in enabled and not (root / ".git").exists():
            subprocess.run(["git", "init", str(root)], check=True, capture_output=True, text=True)
        commands = {"filesystem": filesystem_command(root), "git": git_command(root)}
        for name in enabled:
            if name not in commands:
                raise ValueError(f"Unsupported official MCP server: {name}")
            official_transport = StdioTransport(commands[name], timeout=30, cwd=str(root))
            official_transport.start()
            _active_transports.append(official_transport)
            official_client = MCPClient(official_transport, server_name=f"official-{name}")
            official_client.initialize()
            clients[name] = official_client
            definitions.extend(official_client.list_tools()["tools"])
    if len(clients) == 1:
        return client, definitions
    return MCPClientPool(clients, definitions), definitions
