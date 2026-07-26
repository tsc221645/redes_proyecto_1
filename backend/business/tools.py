from __future__ import annotations

from datetime import date
from typing import Any, Dict

from backend.data_access.repositories import SalesRepository


def _date(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must use YYYY-MM-DD format")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} must use YYYY-MM-DD format") from exc
    return value


class BusinessTools:
    """Validated business operations backed by fixed SQL repository queries."""

    def __init__(self, repository: SalesRepository) -> None:
        self.repository = repository

    def get_sales_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        start_date = _date(arguments.get("start_date"), "start_date")
        end_date = _date(arguments.get("end_date"), "end_date")
        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")
        currency = arguments.get("currency")
        if currency is not None and currency not in {"Q.", "US$"}:
            raise ValueError("currency must be Q. or US$")
        rows = self.repository.query(
            """
            SELECT ANIO, MES,
                   COUNT(DISTINCT SERIE || '-' || CAST(CORRELATIVO AS VARCHAR)) AS total_facturas,
                   SUM(VENTA_NETA_ASIGNADA_LINEA) AS venta_neta,
                   SUM(MARGEN_ESTIMADO_LINEA) AS margen_estimado,
                   SUM(MARGEN_ESTIMADO_LINEA) /
                       NULLIF(SUM(VENTA_NETA_ASIGNADA_LINEA), 0) AS margen_porcentual,
                   SUM(VENTA_NETA_ASIGNADA_LINEA) /
                       NULLIF(COUNT(DISTINCT SERIE || '-' || CAST(CORRELATIVO AS VARCHAR)), 0) AS ticket_promedio
            FROM V_LINEAS_FACTURADAS_ANALITICAS
            WHERE FECHA_INGRESO BETWEEN ? AND ?
              AND (? IS NULL OR MONEDA = ?)
            GROUP BY ANIO, MES
            ORDER BY ANIO, MES
            """,
            (start_date, end_date, currency, currency),
        )
        return {"start_date": start_date, "end_date": end_date, "currency": currency or "Q.", "rows": rows}

    def compare_periods(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        first = arguments.get("first_period")
        second = arguments.get("second_period")
        if not isinstance(first, dict) or not isinstance(second, dict):
            raise ValueError("first_period and second_period are required objects")
        first_result = self.get_sales_summary(first)
        second_result = self.get_sales_summary(second)
        return {"first_period": first_result, "second_period": second_result}

    def analyze_product_performance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        start_date = _date(arguments.get("start_date"), "start_date")
        end_date = _date(arguments.get("end_date"), "end_date")
        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")
        product_code = arguments.get("product_code")
        line_code = arguments.get("line_code")
        if not product_code and not line_code:
            raise ValueError("product_code or line_code is required")
        rows = self.repository.query(
            """
            SELECT CODIGO_PT, DESCRIPCION, MARCA, LINEA, NOMBRE_LINEA, PAIS,
                   SUM(VENTA_NETA_ASIGNADA_LINEA) AS venta_neta,
                   SUM(COSTO_ESTIMADO_LINEA) AS costo_estimado,
                   SUM(MARGEN_ESTIMADO_LINEA) AS margen_estimado,
                   SUM(MARGEN_ESTIMADO_LINEA) /
                       NULLIF(SUM(VENTA_NETA_ASIGNADA_LINEA), 0) AS margen_porcentual,
                   SUM(CANTIDAD_CONVERTIDA) AS cantidad_total,
                   COUNT(DISTINCT SERIE || '-' || CAST(CORRELATIVO AS VARCHAR)) AS facturas_con_producto
            FROM V_LINEAS_FACTURADAS_ANALITICAS
            WHERE FECHA_INGRESO BETWEEN ? AND ?
              AND (? IS NULL OR CODIGO_PT = ?)
              AND (? IS NULL OR LINEA = ?)
            GROUP BY CODIGO_PT, DESCRIPCION, MARCA, LINEA, NOMBRE_LINEA, PAIS
            ORDER BY venta_neta DESC
            """,
            (start_date, end_date, product_code, product_code, line_code, line_code),
        )
        return {"start_date": start_date, "end_date": end_date, "rows": rows}

    def handlers(self) -> Dict[str, Any]:
        """Return the exact tool handlers to register in an MCP server."""
        return {
            "get_sales_summary": self.get_sales_summary,
            "compare_periods": self.compare_periods,
            "analyze_product_performance": self.analyze_product_performance,
        }
