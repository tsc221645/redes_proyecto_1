"""Launch configurations for the official reference Filesystem and Git servers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List


def filesystem_command(allowed_directory: str | Path) -> List[str]:
    """Build the Windows-compatible command for the official Filesystem server."""
    return ["cmd", "/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", str(Path(allowed_directory).resolve())]


def git_command(repository: str | Path) -> List[str]:
    """Build the command for the official Python Git server."""
    return ["uvx", "mcp-server-git", "--repository", str(Path(repository).resolve())]


def server_environment() -> dict[str, str]:
    """Return a minimal environment without exposing application secrets."""
    return {"PATH": os.environ.get("PATH", "")}
