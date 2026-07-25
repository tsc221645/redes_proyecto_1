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

    # Basic validation of jsonrpc field
    if obj.get("jsonrpc") != "2.0":
        raise ValueError("Invalid jsonrpc version; must be '2.0'")

    if "method" in obj:
        return "request", obj
    if "result" in obj or "error" in obj:
        return "response", obj

    raise ValueError("Invalid Request: neither request nor response")
