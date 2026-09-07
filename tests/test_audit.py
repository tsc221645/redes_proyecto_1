import json

from backend.mcp_core.audit import JSONRPCAuditLogger


def test_audit_logger_excludes_secret_fields(tmp_path):
    path = tmp_path / "audit.jsonl"
    JSONRPCAuditLogger(str(path)).record(direction="request", message={"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "x", "arguments": {"password": "secret", "start_date": "2025-01-01"}}})
    content = path.read_text(encoding="utf-8")
    assert "secret" not in content
    assert "start_date" in content


def test_audit_logger_records_both_directions(tmp_path):
    path = tmp_path / "audit.jsonl"
    logger = JSONRPCAuditLogger(str(path))
    message = {"jsonrpc": "2.0", "id": "abc", "method": "tools/list"}
    logger.record(direction="client_to_server", message=message, server="demo", transport="stdio")
    logger.record(direction="server_to_client", message={"jsonrpc": "2.0", "id": "abc", "result": {}}, server="demo", transport="stdio")
    content = path.read_text(encoding="utf-8")
    assert "client_to_server" in content
    assert "server_to_client" in content
    assert "demo" in content
