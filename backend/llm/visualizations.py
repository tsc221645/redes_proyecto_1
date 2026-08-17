from __future__ import annotations

from typing import Any, Dict, List


def build_visualization(tool_name: str, result: Any) -> Dict[str, Any] | None:
    """Create a safe chart payload from known structured tool results."""
    if isinstance(result, dict) and isinstance(result.get("structuredContent"), dict):
        result = result["structuredContent"]
    if not isinstance(result, dict) or not isinstance(result.get("rows"), list) or not result["rows"]:
        return None
    rows: List[Dict[str, Any]] = result["rows"]
    if tool_name in {"get_sales_summary", "query_business_metrics"}:
        if "ANIO" in rows[0] or "year" in rows[0]:
            labels = [f"{row.get('ANIO', row.get('year', ''))}-{int(row.get('MES', row.get('month', 0))):02d}" for row in rows]
            sales_key, margin_key = ("venta_neta", "margen_estimado") if "venta_neta" in rows[0] else ("sales", "margin")
            return {"type": "line", "title": "Ventas y margen por periodo", "labels": labels, "datasets": [{"label": "Venta neta", "data": [row.get(sales_key, 0) for row in rows]}, {"label": "Margen estimado", "data": [row.get(margin_key, 0) for row in rows]}]}
    dimensions = [key for key in ("client", "brand", "line", "product_name", "country") if key in rows[0]]
    if dimensions and any(key in rows[0] for key in ("sales", "units", "margin")):
        dimension = dimensions[0]
        metric = "sales" if "sales" in rows[0] else "units" if "units" in rows[0] else "margin"
        return {"type": "bar", "title": "Rendimiento por " + dimension.replace("_", " "), "labels": [str(row.get(dimension, "Sin dato")) for row in rows], "datasets": [{"label": metric.replace("_", " ").title(), "data": [row.get(metric, 0) for row in rows]}]}
    return None
