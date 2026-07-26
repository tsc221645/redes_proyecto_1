from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any, Dict

from .client import MCPClient
from .official_servers import filesystem_command, git_command
from .stdio_client import StdioTransport


def discover_tools(client: MCPClient) -> list[str]:
    """Initialize a server and return the names it publishes."""
    client.initialize()
    return [tool["name"] for tool in client.list_tools()["tools"]]


def run_filesystem_git_scenario(workspace: str | Path) -> Dict[str, Any]:
    """Run the Phase 4 scenario using two official MCP servers.

    The function intentionally uses server-published tool names and raises a
    clear error if a server version does not expose the expected operation.
    """
    root = Path(workspace).resolve()
    root.mkdir(parents=True, exist_ok=True)
    readme = root / "README.md"

    # mcp-server-git validates that its repository already exists at startup.
    # Repository creation itself is therefore done by Git before launching it;
    # all subsequent Git operations still go through the MCP server.
    subprocess.run(["git", "init", str(root)], check=True, capture_output=True, text=True)

    filesystem_transport = StdioTransport(filesystem_command(root), timeout=30, cwd=str(root))
    git_transport = StdioTransport(git_command(root), timeout=30, cwd=str(root))
    try:
        filesystem_transport.start()
        git_transport.start()
        filesystem = MCPClient(filesystem_transport)
        git = MCPClient(git_transport)
        filesystem_tools = discover_tools(filesystem)
        git_tools = discover_tools(git)
        required_filesystem = {"write_file"}
        required_git = {"git_add", "git_commit"}
        missing = (required_filesystem - set(filesystem_tools)) | (required_git - set(git_tools))
        if missing:
            raise RuntimeError(f"Official server is missing expected tools: {sorted(missing)}")

        filesystem.call_tool("write_file", {"path": str(readme), "content": "# Phase 4 MCP demo\n"})
        git.call_tool("git_add", {"repo_path": str(root), "files": [str(readme)]})
        commit = git.call_tool("git_commit", {
            "repo_path": str(root),
            "message": "docs: add MCP integration demo",
        })
        return {"filesystem_tools": filesystem_tools, "git_tools": git_tools, "commit": commit}
    finally:
        filesystem_transport.close()
        git_transport.close()
