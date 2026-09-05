from __future__ import annotations

from typing import Any, Dict

import httpx


class HTTPTransport:
    """Synchronous JSON-RPC transport for a remote MCP endpoint."""

    def __init__(self, url: str, *, token: str = "", timeout: float = 60.0) -> None:
        self.url = url
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def send(self, message: Dict[str, Any]) -> Dict[str, Any] | None:
        response = httpx.post(self.url, json=message, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        if not response.content:
            return None
        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError("Remote MCP response must be a JSON object")
        return payload
