import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.mcp_core.mcp.client import MCPClient
from backend.mcp_core.mcp.demo_server import create_demo_server


class InMemoryTransport:
    def __init__(self):
        self.server = create_demo_server()

    def send(self, message):
        return self.server.handle(message)


def test_initialize_and_list_tools():
    client = MCPClient(InMemoryTransport())
    result = client.initialize()
    assert result["serverInfo"]["name"] == "demo-mcp-server"
    tools = client.list_tools()["tools"]
    assert {tool["name"] for tool in tools} == {"echo", "add_numbers", "get_server_status"}


def test_call_echo_and_add_numbers():
    client = MCPClient(InMemoryTransport())
    client.initialize()
    assert client.call_tool("echo", {"text": "hello"})["content"][0]["text"] == "hello"
    assert client.call_tool("add_numbers", {"a": 2, "b": 3})["content"][0]["text"] == "5"


def test_unknown_tool_returns_jsonrpc_error():
    response = InMemoryTransport().server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "missing", "arguments": {}},
    })
    assert response["error"]["code"] == -32601


def test_invalid_tool_arguments_return_jsonrpc_error():
    response = InMemoryTransport().server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "add_numbers", "arguments": {"a": "x", "b": 3}},
    })
    assert response["error"]["code"] == -32602


def test_unknown_method_returns_jsonrpc_error():
    response = InMemoryTransport().server.handle({"jsonrpc": "2.0", "id": 1, "method": "unknown"})
    assert response["error"]["code"] == -32601


def test_server_rejects_invalid_jsonrpc_version():
    response = InMemoryTransport().server.handle({"jsonrpc": "1.0", "id": 1, "method": "tools/list"})
    assert response["error"]["code"] == -32600


def test_notification_has_no_response():
    response = InMemoryTransport().server.handle({"jsonrpc": "2.0", "method": "unknown"})
    assert response is None


def test_client_rejects_mismatched_response_id():
    class BadTransport:
        def send(self, message):
            if "id" not in message:
                return None
            return {"jsonrpc": "2.0", "id": "different", "result": {}}

    client = MCPClient(BadTransport())
    with pytest.raises(RuntimeError, match="mismatched"):
        client.list_tools()
