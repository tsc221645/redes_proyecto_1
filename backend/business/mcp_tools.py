from __future__ import annotations

from backend.data_access.config import SQLAnywhereSettings
from backend.data_access.repositories import SalesRepository
from backend.data_access.sqlanywhere import SQLAnywhereConnection
from backend.mcp_core.mcp.types import MCPTool
from .tools import BusinessTools


def create_business_mcp_tools(settings: SQLAnywhereSettings) -> list[MCPTool]:
    """Create the first three database-backed MCP tools."""
    use_cases = BusinessTools(SalesRepository(SQLAnywhereConnection(settings)))
    return [
        MCPTool("get_sales_summary", "Summarize real sales by month. Dates must be strings in YYYY-MM-DD format.", {"type": "object", "required": ["start_date", "end_date"], "properties": {"start_date": {"type": "string", "format": "date"}, "end_date": {"type": "string", "format": "date"}, "currency": {"type": "string", "enum": ["Q.", "US$"]}}}, use_cases.get_sales_summary),
        MCPTool("compare_periods", "Compare sales metrics for two periods. Every date must be a YYYY-MM-DD string.", {"type": "object", "required": ["first_period", "second_period"], "properties": {"first_period": {"type": "object"}, "second_period": {"type": "object"}}}, use_cases.compare_periods),
        MCPTool("analyze_product_performance", "Analyze product or product-line performance. Dates must be strings in YYYY-MM-DD format.", {"type": "object", "required": ["start_date", "end_date"], "properties": {"start_date": {"type": "string", "format": "date"}, "end_date": {"type": "string", "format": "date"}, "product_code": {"type": "string"}, "line_code": {"type": "string"}}}, use_cases.analyze_product_performance),
    ]
