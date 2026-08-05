from __future__ import annotations

from datetime import date
from typing import Any, Dict

from backend.data_access.repositories import SalesRepository


def _date(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must use YYYY-MM-DD format")
    value = value.strip()
    if "T" in value:
        value = value.split("T", 1)[0]
    if value.count("/") == 2:
        parts = value.split("/")
        if len(parts[0]) == 4:
            value = "-".join(parts)
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
        query = """
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
        """
        parameters: list[Any] = [start_date, end_date]
        if currency is not None:
            query += " AND MONEDA = ?\n"
            parameters.append(currency)
        query += """
            GROUP BY ANIO, MES
            ORDER BY ANIO, MES
        """
        rows = self.repository.query(query, tuple(parameters))
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
        product_name = arguments.get("product_name")
        line_code = arguments.get("line_code")
        if not product_code and not product_name and not line_code:
            raise ValueError("product_code, product_name or line_code is required")
        rows = self.repository.query(
            """
            SELECT v.CODIGO_PT, v.DESCRIPCION, v.MARCA, v.LINEA, l.NOMBRE AS NOMBRE_LINEA, v.PAIS,
                   SUM(v.VENTA_NETA_ASIGNADA_LINEA) AS venta_neta,
                   SUM(v.COSTO_ESTIMADO_LINEA) AS costo_estimado,
                   SUM(v.MARGEN_ESTIMADO_LINEA) AS margen_estimado,
                   SUM(v.MARGEN_ESTIMADO_LINEA) /
                       NULLIF(SUM(v.VENTA_NETA_ASIGNADA_LINEA), 0) AS margen_porcentual,
                   SUM(v.CANTIDAD_CONVERTIDA) AS cantidad_total,
                   COUNT(DISTINCT v.SERIE || '-' || CAST(v.CORRELATIVO AS VARCHAR)) AS facturas_con_producto
            FROM V_LINEAS_FACTURADAS_ANALITICAS v
            LEFT JOIN PT_LINEAS l ON v.LINEA = l.LINEA
            WHERE v.FECHA_INGRESO BETWEEN ? AND ?
              AND (? IS NULL OR v.CODIGO_PT = ?)
              AND (? IS NULL OR v.DESCRIPCION = ?)
              AND (? IS NULL OR v.LINEA = ?)
            GROUP BY v.CODIGO_PT, v.DESCRIPCION, v.MARCA, v.LINEA, l.NOMBRE, v.PAIS
            ORDER BY venta_neta DESC
            """,
            (start_date, end_date, product_code, product_code, product_name, product_name, line_code, line_code),
        )
        return {"start_date": start_date, "end_date": end_date, "rows": rows}

    def handlers(self) -> Dict[str, Any]:
        """Return the exact tool handlers to register in an MCP server."""
        return {
            "get_sales_summary": self.get_sales_summary,
            "compare_periods": self.compare_periods,
            "analyze_product_performance": self.analyze_product_performance,
        }

    def query_business_metrics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Answer bounded analytical questions without allowing arbitrary SQL."""
        start_date = _date(arguments.get("start_date"), "start_date")
        end_date = _date(arguments.get("end_date"), "end_date")
        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")

        dimensions = {
            "year": "v.ANIO", "month": "v.MES", "product_code": "v.CODIGO_PT",
            "product_name": "v.DESCRIPCION", "brand": "pm.NOMBRE", "line": "v.LINEA",
            "country": "v.PAIS", "client": "pc.NOMBRE_CLIENTE", "currency": "v.MONEDA",
        }
        measures = {
            "sales": "SUM(v.VENTA_NETA_ASIGNADA_LINEA)",
            "gross_sales": "SUM(v.VENTA_BRUTA_LINEA)",
            "cost": "SUM(v.COSTO_ESTIMADO_LINEA)",
            "margin": "SUM(v.MARGEN_ESTIMADO_LINEA)",
            "units": "SUM(v.CANTIDAD_CONVERTIDA)",
            "invoice_count": "COUNT(DISTINCT v.SERIE || '-' || CAST(v.CORRELATIVO AS VARCHAR))",
            "line_count": "COUNT(*)",
        }
        requested_dimensions = arguments.get("group_by", ["year", "month"])
        requested_measures = arguments.get("metrics", ["sales", "margin"])
        if not isinstance(requested_dimensions, list) or not requested_dimensions:
            raise ValueError("group_by must contain at least one dimension")
        if not isinstance(requested_measures, list) or not requested_measures:
            raise ValueError("metrics must contain at least one metric")
        unknown_dimensions = set(requested_dimensions) - dimensions.keys()
        unknown_measures = set(requested_measures) - measures.keys()
        if unknown_dimensions:
            raise ValueError(f"Unsupported dimensions: {sorted(unknown_dimensions)}")
        if unknown_measures:
            raise ValueError(f"Unsupported metrics: {sorted(unknown_measures)}")
        if len(requested_dimensions) > 4 or len(requested_measures) > 7:
            raise ValueError("Too many dimensions or metrics requested")

        select_parts = [f"{dimensions[item]} AS {item}" for item in requested_dimensions]
        select_parts += [f"{measures[item]} AS {item}" for item in requested_measures]
        limit = arguments.get("limit", 100)
        if not isinstance(limit, int) or not 1 <= limit <= 500:
            raise ValueError("limit must be an integer between 1 and 500")
        query = "SELECT TOP ? " + ", ".join(select_parts) + " FROM V_LINEAS_FACTURADAS_ANALITICAS v LEFT JOIN PT_MARCAS pm ON v.MARCA = pm.MARCA LEFT JOIN PT_CLIENTES pc ON v.CLIENTE = pc.CLIENTE WHERE v.FECHA_INGRESO BETWEEN ? AND ?"
        parameters: list[Any] = [limit, start_date, end_date]
        filter_map = {"product_code": "v.CODIGO_PT", "product_name": "v.DESCRIPCION", "line_code": "v.LINEA", "brand_code": "v.MARCA", "country_code": "v.PAIS", "client_code": "v.CLIENTE", "currency": "v.MONEDA"}
        for argument, column in filter_map.items():
            if arguments.get(argument) is not None:
                value = arguments[argument]
                if argument == "product_name":
                    query += " AND UPPER(v.DESCRIPCION) LIKE UPPER(?)"
                    parameters.append(f"%{value}%")
                else:
                    query += f" AND {column} = ?"
                    parameters.append(value)
        group_sql = ", ".join(dimensions[item] for item in requested_dimensions)
        query += f" GROUP BY {group_sql}"
        order_by = arguments.get("order_by", "sales")
        if order_by not in requested_measures:
            raise ValueError("order_by must be one of the selected metrics")
        query += f" ORDER BY {order_by} DESC"
        rows = self.repository.query(query, tuple(parameters))
        return {"start_date": start_date, "end_date": end_date, "rows": rows}
