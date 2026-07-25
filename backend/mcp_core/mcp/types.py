from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass(frozen=True)
class ServerInfo:
    name: str
    version: str


@dataclass(frozen=True)
class ServerCapabilities:
    tools: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[ToolHandler] = None

    def public_definition(self) -> Dict[str, Any]:
        """Return the tool metadata exposed to MCP clients."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }
