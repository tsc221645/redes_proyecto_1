"""Line-delimited stdio entry point for the Phase 3 demo MCP server."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from .demo_server import create_demo_server


def run() -> None:
    """Read JSON-RPC messages from stdin and write responses to stdout."""
    server = create_demo_server()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("message must be an object")
            response = server.handle(message)
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except (json.JSONDecodeError, ValueError) as exc:
            response: Dict[str, Any] = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as exc:  # Keep protocol output valid if the process hits an unexpected error.
            print(f"stdio server error: {exc}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    run()
