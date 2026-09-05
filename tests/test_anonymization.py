from backend.data_access.anonymization import StableAnonymizer


def test_anonymization_is_stable_and_type_scoped():
    anonymizer = StableAnonymizer("test-salt")
    first = anonymizer.anonymize("A-001", "client")
    assert first == anonymizer.anonymize("A-001", "client")
    assert first != anonymizer.anonymize("A-001", "product")
    assert anonymizer.anonymize(None, "client") is None


def test_transform_row_preserves_non_sensitive_columns():
    row = {"CLIENTE": "A-001", "VENTA": 10}
    result = StableAnonymizer("test-salt").transform_row(row, {"CLIENTE": "client"})
    assert result["CLIENTE"].startswith("Cliente_")
    assert result["VENTA"] == 10
