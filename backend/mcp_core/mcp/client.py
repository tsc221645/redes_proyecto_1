from __future__ import annotations

from typing import Any, Dict, Protocol

from backend.mcp_core.jsonrpc import generate_id
from backend.mcp_core.audit import JSONRPCAuditLogger, monotonic_ms


class MCPTransport(Protocol):
    def send(self, message: Dict[str, Any]) -> Dict[str, Any] | None: ...


class MCPClient:
    """Manual MCP client using a synchronous request/response transport."""

    def __init__(self, transport: MCPTransport, *, server_name: str = "unknown", audit_logger: JSONRPCAuditLogger | None = None) -> None:
        self.transport = transport
        self.server_name = server_name
        self.audit = audit_logger or JSONRPCAuditLogger()
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
        started = monotonic_ms()
        self.audit.record(direction="client_to_server", message=message, server=self.server_name, transport=type(self.transport).__name__)
        try:
            response = self.transport.send(message)
        except Exception as exc:
            self.audit.record(direction="client_error", message=message, duration_ms=monotonic_ms() - started, error=str(exc), server=self.server_name, transport=type(self.transport).__name__)
            raise
        if response is None:
            error = f"No response received for {method}"
            self.audit.record(direction="client_error", message=message, duration_ms=monotonic_ms() - started, error=error, server=self.server_name, transport=type(self.transport).__name__)
            raise RuntimeError(error)
        self.audit.record(direction="server_to_client", message=response, duration_ms=monotonic_ms() - started, error=response.get("error", {}).get("message") if response.get("error") else None, server=self.server_name, transport=type(self.transport).__name__)
        if response.get("jsonrpc") != "2.0" or response.get("id") != message["id"] or ("result" not in response and "error" not in response):
            raise RuntimeError(f"Invalid or mismatched JSON-RPC response for {method}")
        if "error" in response:
            raise RuntimeError(response["error"]["message"])
        return response["result"]

    def notify(self, method: str) -> None:
        message = {"jsonrpc": "2.0", "method": method}
        self.audit.record(direction="client_to_server", message=message, server=self.server_name, transport=type(self.transport).__name__)
        self.transport.send(message)
