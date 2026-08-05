from __future__ import annotations

from typing import Iterable

from backend.mcp_core.mcp.types import MCPTool


class BusinessToolRegistry:
    """Central catalog for business tools, avoiding changes to orchestration code."""

    def __init__(self, tools: Iterable[MCPTool] = ()) -> None:
        self._tools: dict[str, MCPTool] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: MCPTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Duplicate business tool: {tool.name}")
        self._tools[tool.name] = tool

    def all(self) -> list[MCPTool]:
        return list(self._tools.values())
