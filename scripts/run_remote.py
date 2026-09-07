"""Run the remote MCP HTTP service with optional, configurable TLS."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    cert = os.getenv("MCP_TLS_CERTFILE")
    key = os.getenv("MCP_TLS_KEYFILE")
    required = os.getenv("MCP_TLS_REQUIRED", "false").lower() == "true"
    if required and (not cert or not key):
        raise SystemExit("MCP_TLS_REQUIRED=true requires MCP_TLS_CERTFILE and MCP_TLS_KEYFILE")
    uvicorn.run(
        "backend.business.remote_server:app",
        host=os.getenv("MCP_BIND_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_BIND_PORT", "8080")),
        ssl_certfile=cert,
        ssl_keyfile=key,
    )


if __name__ == "__main__":
    main()
