from __future__ import annotations

from typing import Any, Dict, Iterable

from backend.mcp_core.jsonrpc import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    METHOD_NOT_FOUND,
    make_error_object,
)
from .types import MCPTool, ServerCapabilities, ServerInfo


class MCPServer:
    """Small MCP server implementing the Phase 2 lifecycle and tools methods."""

    def __init__(self, info: ServerInfo, tools: Iterable[MCPTool]) -> None:
        self.info = info
        self.capabilities = ServerCapabilities(tools={})
        self._tools = {tool.name: tool for tool in tools}

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any] | None:
        """Process one JSON-RPC message and return its response, if any."""
        request_id = message.get("id")
        method = message.get("method")
        if not isinstance(method, str):
            return self._error(request_id, -32600, "Invalid Request")

        if method == "notifications/initialized":
            return None
        if method == "initialize":
            return self._success(request_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": self.capabilities.tools},
                "serverInfo": {"name": self.info.name, "version": self.info.version},
            })
        if method == "tools/list":
            return self._success(request_id, {
                "tools": [tool.public_definition() for tool in self._tools.values()]
            })
        if method == "tools/call":
            return self._call_tool(request_id, message.get("params"))
        return self._error(request_id, METHOD_NOT_FOUND, f"Method not found: {method}")

    def _call_tool(self, request_id: Any, params: Any) -> Dict[str, Any]:
        if not isinstance(params, dict) or not isinstance(params.get("name"), str):
            return self._error(request_id, INVALID_PARAMS, "tools/call requires a tool name")
        tool = self._tools.get(params["name"])
        if tool is None:
            return self._error(request_id, METHOD_NOT_FOUND, f"Tool not found: {params['name']}")
        arguments = params.get("arguments", {})
        if not isinstance(arguments, dict):
            return self._error(request_id, INVALID_PARAMS, "Tool arguments must be an object")
        try:
            if tool.handler is None:
                raise RuntimeError(f"Tool has no handler: {tool.name}")
            result = tool.handler(arguments)
            return self._success(request_id, {"content": [{"type": "text", "text": result}]})
        except ValueError as exc:
            return self._error(request_id, INVALID_PARAMS, str(exc))
        except Exception:
            return self._error(request_id, INTERNAL_ERROR, "Internal tool error")

    @staticmethod
    def _success(request_id: Any, result: Any) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": make_error_object(code, message)}
