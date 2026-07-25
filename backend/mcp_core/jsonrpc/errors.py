from __future__ import annotations

from typing import Any, Dict, Optional

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


def make_error_object(code: int, message: str, data: Optional[Any] = None) -> Dict[str, Any]:
    """Create a JSON-RPC error object dictionary."""
    obj = {"code": code, "message": message}
    if data is not None:
        obj["data"] = data
    return obj
