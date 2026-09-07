import pytest

from backend.mcp_core.mcp.http_transport import HTTPTransport


def test_http_transport_can_require_tls(monkeypatch):
    monkeypatch.setenv("MCP_REQUIRE_TLS", "true")
    with pytest.raises(ValueError):
        HTTPTransport("http://127.0.0.1:8080/mcp")
    assert HTTPTransport("https://127.0.0.1:8080/mcp").url.startswith("https://")
