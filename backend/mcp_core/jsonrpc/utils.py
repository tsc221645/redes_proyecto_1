from __future__ import annotations

import json
import uuid
from typing import Any, Dict, Tuple

from .messages import JSONRPCRequest, JSONRPCResponse
from .errors import PARSE_ERROR, INVALID_REQUEST


def generate_id() -> str:
    """Generate a short unique identifier for requests."""
    return uuid.uuid4().hex


def serialize_message(message: Dict[str, Any]) -> str:
    """Serialize a JSON-RPC message to a compact JSON string."""
    return json.dumps(message, ensure_ascii=False)


def validate_request(obj: Dict[str, Any]) -> None:
    """Validate the JSON-RPC 2.0 request shape used by MCP."""
    if obj.get("jsonrpc") != "2.0" or not isinstance(obj.get("method"), str) or not obj["method"]:
        raise ValueError("Invalid Request")
    if "id" in obj and (obj["id"] is None or isinstance(obj["id"], bool) or not isinstance(obj["id"], (str, int))):
        raise ValueError("Invalid Request id")
    if "params" in obj and not isinstance(obj["params"], (dict, list)):
        raise ValueError("Invalid Request params")


def validate_response(obj: Dict[str, Any]) -> None:
    """Validate the JSON-RPC response shape and result/error exclusivity."""
    if obj.get("jsonrpc") != "2.0" or "id" not in obj:
        raise ValueError("Invalid Response")
    if ("result" in obj) == ("error" in obj):
        raise ValueError("Response must contain exactly one of result or error")
    if "error" in obj:
        error = obj["error"]
        if not isinstance(error, dict) or not isinstance(error.get("code"), int) or not isinstance(error.get("message"), str):
            raise ValueError("Invalid Response error")


def parse_message(raw: str) -> Tuple[str, Dict[str, Any]]:
    """Parse raw JSON text into a dict and determine message type.

    Returns a tuple (type, payload) where type is 'request', 'response' or 'invalid'.
    Raises ValueError for parse errors.
    """
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Parse error: {exc.msg}") from exc

    if not isinstance(obj, dict):
        raise ValueError("Invalid Request: top-level must be an object")

    if "method" in obj:
        validate_request(obj)
        return "request", obj
    if "result" in obj or "error" in obj:
        validate_response(obj)
        return "response", obj

    raise ValueError("Invalid Request: neither request nor response")
