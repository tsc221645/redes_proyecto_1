from __future__ import annotations

from typing import Any, Dict, Protocol

from backend.mcp_core.jsonrpc import generate_id


class MCPTransport(Protocol):
    def send(self, message: Dict[str, Any]) -> Dict[str, Any] | None: ...


class MCPClient:
    """Manual MCP client using a synchronous request/response transport."""

    def __init__(self, transport: MCPTransport) -> None:
        self.transport = transport
        self.initialized = False

    def initialize(self) -> Dict[str, Any]:
        response = self.request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "phase2-client", "version": "0.1.0"},
        })
        self.notify("notifications/initialized")
        self.initialized = True
        return response

    def list_tools(self) -> Dict[str, Any]:
        return self.request("tools/list")

    def call_tool(self, name: str, arguments: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return self.request("tools/call", {"name": name, "arguments": arguments or {}})

    def request(self, method: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        message: Dict[str, Any] = {"jsonrpc": "2.0", "id": generate_id(), "method": method}
        if params is not None:
            message["params"] = params
        response = self.transport.send(message)
        if response is None:
            raise RuntimeError(f"No response received for {method}")
        if "error" in response:
            raise RuntimeError(response["error"]["message"])
        return response["result"]

    def notify(self, method: str) -> None:
        self.transport.send({"jsonrpc": "2.0", "method": method})
