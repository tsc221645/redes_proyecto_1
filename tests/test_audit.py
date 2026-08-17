import json

from backend.mcp_core.audit import JSONRPCAuditLogger


def test_audit_logger_excludes_secret_fields(tmp_path):
    path = tmp_path / "audit.jsonl"
    JSONRPCAuditLogger(str(path)).record(direction="request", message={"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "x", "arguments": {"password": "secret", "start_date": "2025-01-01"}}})
    content = path.read_text(encoding="utf-8")
    assert "secret" not in content
    assert "start_date" in content
