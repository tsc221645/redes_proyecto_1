import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.business.tools import BusinessTools


class FakeRepository:
    def query(self, sql, parameters):
        return [{"rows": 1, "parameters": parameters}]


def test_sales_summary_validates_dates_and_currency():
    tools = BusinessTools(FakeRepository())
    result = tools.get_sales_summary({"start_date": "2025-01-01", "end_date": "2025-03-31", "currency": "Q."})
    assert result["currency"] == "Q."
    with pytest.raises(ValueError):
        tools.get_sales_summary({"start_date": "2025-04-01", "end_date": "2025-01-01"})


def test_compare_periods_requires_two_periods():
    tools = BusinessTools(FakeRepository())
    with pytest.raises(ValueError):
        tools.compare_periods({})


def test_product_performance_requires_product_or_line():
    tools = BusinessTools(FakeRepository())
    with pytest.raises(ValueError):
        tools.analyze_product_performance({"start_date": "2025-01-01", "end_date": "2025-01-31"})
    result = tools.analyze_product_performance({"start_date": "2025-01-01", "end_date": "2025-01-31", "line_code": "01"})
    assert result["rows"]


def test_general_metrics_tool_restricts_dimensions_and_limit():
    tools = BusinessTools(FakeRepository())
    result = tools.query_business_metrics({
        "start_date": "2025-01-01", "end_date": "2025-12-31",
        "group_by": ["line"], "metrics": ["sales", "margin"], "limit": 10,
    })
    assert result["rows"]
    with pytest.raises(ValueError):
        tools.query_business_metrics({"start_date": "2025-01-01", "end_date": "2025-12-31", "group_by": ["sql"]})
