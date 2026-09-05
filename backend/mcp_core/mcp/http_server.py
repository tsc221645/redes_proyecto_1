from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import FastAPI, Header, HTTPException

from backend.data_access.config import SQLAnywhereSettings
from backend.mcp_core.audit import JSONRPCAuditLogger, monotonic_ms
from .server import MCPServer
from .types import ServerInfo


def create_http_mcp_app(server: MCPServer | None = None) -> FastAPI:
    app = FastAPI(title="Executive Insights MCP")
    mcp_server = server or _build_business_server()
    audit = JSONRPCAuditLogger()
    expected_token = os.getenv("MCP_REMOTE_TOKEN", "")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "mcp"}

    @app.post("/mcp")
    def mcp_endpoint(message: Dict[str, Any], authorization: str | None = Header(default=None)) -> Dict[str, Any]:
        if expected_token and authorization != f"Bearer {expected_token}":
            raise HTTPException(status_code=401, detail="Invalid MCP token")
        started = monotonic_ms()
        response = mcp_server.handle(message)
        audit.record(direction="request", message=message, duration_ms=monotonic_ms() - started)
        if response is None:
            return {"jsonrpc": "2.0", "result": None}
        audit.record(
            direction="response",
            message=response,
            duration_ms=monotonic_ms() - started,
            error=response.get("error", {}).get("message") if response.get("error") else None,
        )
        return response

    return app


def _build_business_server() -> MCPServer:
    from backend.business.mcp_tools import create_business_mcp_tools

    remote_url = os.getenv("REMOTE_DATABASE_URL")
    if remote_url:
        from backend.data_access.postgres import PostgresRepository

        return MCPServer(ServerInfo("business-mcp-remote", "1.0.0"), create_business_mcp_tools(repository=PostgresRepository(remote_url)))
    settings = SQLAnywhereSettings.from_env()
    return MCPServer(ServerInfo("business-mcp-remote", "1.0.0"), create_business_mcp_tools(settings))


app = create_http_mcp_app()
