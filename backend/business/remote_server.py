"""HTTP entry point for the remote MCP deployment."""

from backend.mcp_core.mcp.http_server import app

__all__ = ["app"]
