from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class JSONRPCAuditLogger:
    """Append safe JSON-RPC audit events without secrets or full business rows."""

    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or os.getenv("MCP_AUDIT_LOG", "logs/mcp_audit.jsonl"))

    def record(self, *, direction: str, message: Dict[str, Any], duration_ms: float | None = None, error: str | None = None) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "direction": direction,
            "jsonrpc_id": message.get("id"),
            "method": message.get("method"),
            "tool": self._tool_name(message),
            "parameters": self._safe_parameters(message.get("params")),
            "duration_ms": round(duration_ms, 2) if duration_ms is not None else None,
            "error": error,
        }
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")

    @staticmethod
    def _tool_name(message: Dict[str, Any]) -> str | None:
        params = message.get("params")
        return params.get("name") if isinstance(params, dict) else None

    @staticmethod
    def _safe_parameters(params: Any) -> Any:
        if not isinstance(params, dict):
            return None
        safe = dict(params)
        if "arguments" in safe and isinstance(safe["arguments"], dict):
            safe["arguments"] = {key: value for key, value in safe["arguments"].items() if key not in {"password", "token", "api_key", "connection_string"}}
        return safe


def monotonic_ms() -> float:
    return time.perf_counter() * 1000
