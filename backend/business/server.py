"""Standalone local business MCP server using newline-delimited stdio."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from backend.data_access.config import SQLAnywhereSettings
from backend.mcp_core.audit import JSONRPCAuditLogger, monotonic_ms
from backend.mcp_core.mcp.server import MCPServer
from backend.mcp_core.mcp.types import ServerInfo
from .mcp_tools import create_business_mcp_tools


def run() -> None:
    settings = SQLAnywhereSettings.from_env()
    server = MCPServer(ServerInfo("business-mcp-server", "1.0.0"), create_business_mcp_tools(settings))
    audit = JSONRPCAuditLogger()
    for line in sys.stdin:
        if not line.strip():
            continue
        started = monotonic_ms()
        request: Dict[str, Any] = {}
        try:
            request = json.loads(line)
            if not isinstance(request, dict):
                raise ValueError("JSON-RPC message must be an object")
            response = server.handle(request)
            audit.record(direction="request", message=request, duration_ms=monotonic_ms() - started)
            if response is not None:
                # Escape Unicode on the protocol stream so Windows code pages
                # cannot corrupt JSON-RPC stdout.
                sys.stdout.write(json.dumps(response, ensure_ascii=True, default=str) + "\n")
                sys.stdout.flush()
                audit.record(direction="response", message=response, duration_ms=monotonic_ms() - started, error=response.get("error", {}).get("message") if response.get("error") else None)
        except Exception as exc:
            audit.record(direction="request", message=request, duration_ms=monotonic_ms() - started, error=str(exc))
            response = {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32603, "message": "Internal server error"}}
            sys.stdout.write(json.dumps(response, ensure_ascii=True) + "\n")
            sys.stdout.flush()
            print(f"business MCP server error: {exc}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    run()
