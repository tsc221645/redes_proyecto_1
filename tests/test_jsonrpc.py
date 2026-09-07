import json
import os
import sys
import pytest

# Ensure project root is on sys.path so tests can import the backend package
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.mcp_core.jsonrpc import (
    JSONRPCRequest,
    JSONRPCResponse,
    generate_id,
    parse_message,
    serialize_message,
    make_error_object,
)


def test_generate_id_is_string_and_unique():
    a = generate_id()
    b = generate_id()
    assert isinstance(a, str)
    assert a != b


def test_serialize_and_parse_request():
    req = {"jsonrpc": "2.0", "method": "echo", "params": {"text": "hi"}, "id": "1"}
    s = serialize_message(req)
    t, obj = parse_message(s)
    assert t == "request"
    assert obj["method"] == "echo"


def test_notification_without_id_parses_as_request():
    note = {"jsonrpc": "2.0", "method": "notify", "params": {"x": 1}}
    t, obj = parse_message(json.dumps(note))
    assert t == "request"
    assert obj.get("id") is None


def test_response_with_result_parses_as_response():
    resp = {"jsonrpc": "2.0", "id": "1", "result": {"ok": True}}
    t, obj = parse_message(json.dumps(resp))
    assert t == "response"
    assert obj["result"]["ok"] is True


def test_invalid_json_raises():
    with pytest.raises(ValueError):
        parse_message("{invalid json")


def test_invalid_jsonrpc_version_raises():
    with pytest.raises(ValueError):
        parse_message(json.dumps({"jsonrpc": "1.0", "method": "x"}))


def test_make_error_object():
    err = make_error_object(-32601, "Not found", {"method": "x"})
    assert err["code"] == -32601
    assert err["message"] == "Not found"


def test_parse_rejects_invalid_request_shape_and_nonexclusive_response():
    with pytest.raises(ValueError):
        parse_message(json.dumps({"jsonrpc": "2.0", "method": "x", "id": None}))
    with pytest.raises(ValueError):
        parse_message(json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}, "error": {"code": 1, "message": "x"}}))
