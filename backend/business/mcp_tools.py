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
        MCPTool("get_sales_summary", "Summarize real sales by month.", {"type": "object", "required": ["start_date", "end_date"]}, use_cases.get_sales_summary),
        MCPTool("compare_periods", "Compare sales metrics for two periods.", {"type": "object", "required": ["first_period", "second_period"]}, use_cases.compare_periods),
        MCPTool("analyze_product_performance", "Analyze product or product-line performance.", {"type": "object", "required": ["start_date", "end_date"]}, use_cases.analyze_product_performance),
    ]
