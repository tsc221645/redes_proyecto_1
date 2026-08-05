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
        MCPTool("get_customer_product_mix", "Find the customer who buys the most of a product, then list that customer's other products.", {"type": "object", "required": ["start_date", "end_date", "product_name"], "properties": {"start_date": {"type": "string", "format": "date"}, "end_date": {"type": "string", "format": "date"}, "product_name": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 100}}}, use_cases.get_customer_product_mix),
        MCPTool("query_business_metrics", "Answer a bounded business analytics question. Use product_name for descriptions such as 'Car Kool Verde'; use product_code only for actual CODIGO_PT values. For questions about which clients buy a product, set group_by to ['client'] and product_name to the description.", {"type": "object", "required": ["start_date", "end_date"], "properties": {"start_date": {"type": "string", "format": "date"}, "end_date": {"type": "string", "format": "date"}, "group_by": {"type": "array", "items": {"type": "string", "enum": ["year", "month", "product_code", "product_name", "brand", "line", "country", "client", "currency"]}}, "metrics": {"type": "array", "items": {"type": "string", "enum": ["sales", "gross_sales", "cost", "margin", "units", "invoice_count", "line_count"]}}, "product_name": {"type": "string"}, "product_code": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 500}, "order_by": {"type": "string"}}}, use_cases.query_business_metrics),
        MCPTool("get_sales_summary", "Summarize real sales by month. Dates must be strings in YYYY-MM-DD format.", {"type": "object", "required": ["start_date", "end_date"], "properties": {"start_date": {"type": "string", "format": "date"}, "end_date": {"type": "string", "format": "date"}, "currency": {"type": "string", "enum": ["Q.", "US$"]}}}, use_cases.get_sales_summary),
        MCPTool("compare_periods", "Compare sales metrics for two periods. Every date must be a YYYY-MM-DD string.", {"type": "object", "required": ["first_period", "second_period"], "properties": {"first_period": {"type": "object"}, "second_period": {"type": "object"}}}, use_cases.compare_periods),
        MCPTool("analyze_product_performance", "Analyze product or product-line performance. Use product_name for a description and product_code only for an actual code. Dates must be strings in YYYY-MM-DD format.", {"type": "object", "required": ["start_date", "end_date"], "properties": {"start_date": {"type": "string", "format": "date"}, "end_date": {"type": "string", "format": "date"}, "product_code": {"type": "string"}, "product_name": {"type": "string"}, "line_code": {"type": "string"}}}, use_cases.analyze_product_performance),
    ]
