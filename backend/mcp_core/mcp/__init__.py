"""Minimal, manual MCP implementation for Phase 2."""

from .client import MCPClient
from .server import MCPServer
from .stdio_client import StdioTransport
from .types import MCPTool, ServerCapabilities, ServerInfo

__all__ = ["MCPClient", "MCPServer", "MCPTool", "ServerCapabilities", "ServerInfo", "StdioTransport"]
