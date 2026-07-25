from __future__ import annotations

from typing import Any, Dict

from .server import MCPServer
from .types import MCPTool, ServerInfo


def create_demo_server() -> MCPServer:
    """Create the temporary server required by the Phase 2 acceptance criteria."""

    def echo(arguments: Dict[str, Any]) -> str:
        text = arguments.get("text")
        if not isinstance(text, str):
            raise ValueError("'text' must be a string")
        return text

    def add_numbers(arguments: Dict[str, Any]) -> str:
        first, second = arguments.get("a"), arguments.get("b")
        if not isinstance(first, (int, float)) or not isinstance(second, (int, float)):
            raise ValueError("'a' and 'b' must be numbers")
        return str(first + second)

    def get_server_status(arguments: Dict[str, Any]) -> str:
        return "ok"

    return MCPServer(
        ServerInfo(name="demo-mcp-server", version="0.1.0"),
        [
            MCPTool("echo", "Return the supplied text.", {"type": "object"}, echo),
            MCPTool("add_numbers", "Add two numbers.", {"type": "object"}, add_numbers),
            MCPTool("get_server_status", "Return server health status.", {"type": "object"}, get_server_status),
        ],
    )
