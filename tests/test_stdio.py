import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.mcp_core.mcp.client import MCPClient
from backend.mcp_core.mcp.stdio_client import StdioTransport, demo_command


@pytest.fixture
def stdio_client():
    transport = StdioTransport(demo_command(), timeout=3, cwd=ROOT)
    transport.start()
    client = MCPClient(transport)
    yield client
    transport.close()


def test_stdio_initialize_list_and_call(stdio_client):
    result = stdio_client.initialize()
    assert result["serverInfo"]["name"] == "demo-mcp-server"
    assert len(stdio_client.list_tools()["tools"]) == 3
    assert stdio_client.call_tool("echo", {"text": "stdio"})["content"][0]["text"] == "stdio"


def test_stdio_unknown_tool_returns_client_error(stdio_client):
    with pytest.raises(RuntimeError, match="Tool not found"):
        stdio_client.call_tool("missing")


def test_stdio_restart(stdio_client):
    stdio_client.initialize()
    stdio_client.transport.restart()
    assert stdio_client.initialize()["serverInfo"]["version"] == "0.1.0"
