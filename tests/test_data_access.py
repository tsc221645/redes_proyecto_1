import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.data_access.config import SQLAnywhereSettings
from backend.data_access.repositories import SalesRepository


def settings():
    return SQLAnywhereSettings("127.0.0.1", 2638, "TEST_SERVER", "TEST_DATABASE", "reader", "secret", "SQL Anywhere 17")


def test_connection_string_contains_endpoint_and_credentials_for_driver():
    from backend.data_access.sqlanywhere import SQLAnywhereConnection
    connection_string = SQLAnywhereConnection(settings()).connection_string()
    assert "127.0.0.1:2638" in connection_string
    assert "secret" in connection_string


def test_annual_sales_rejects_reversed_period():
    with pytest.raises(ValueError):
        SalesRepository(None).annual_sales(2025, 2024)
