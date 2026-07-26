import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.mcp_core.mcp.official_servers import filesystem_command, git_command


def test_filesystem_command_has_allowed_directory():
    command = filesystem_command("demo")
    assert command[:4] == ["cmd", "/c", "npx", "-y"]
    assert "@modelcontextprotocol/server-filesystem" in command
    assert command[-1].endswith("demo")


def test_git_command_binds_repository():
    command = git_command("demo")
    assert command[:3] == ["uvx", "mcp-server-git", "--repository"]
    assert command[-1].endswith("demo")
