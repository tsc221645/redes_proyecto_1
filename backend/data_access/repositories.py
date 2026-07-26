from __future__ import annotations

from typing import Any, Dict, List

from .sqlanywhere import SQLAnywhereConnection


class SalesRepository:
    """Read-only repository for controlled sales queries."""

    def __init__(self, database: SQLAnywhereConnection) -> None:
        self.database = database

    def annual_sales(self, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        """Return annual sales metrics using bounded, parameterized SQL."""
        if start_year > end_year:
            raise ValueError("start_year must be less than or equal to end_year")
        query = """
            SELECT ANIO,
                   COUNT(DISTINCT SERIE || '-' || CAST(CORRELATIVO AS VARCHAR)) AS total_facturas,
                   SUM(VENTA_NETA_ASIGNADA_LINEA) AS venta_neta,
                   SUM(MARGEN_ESTIMADO_LINEA) AS margen_estimado,
                   SUM(MARGEN_ESTIMADO_LINEA) /
                       NULLIF(SUM(VENTA_NETA_ASIGNADA_LINEA), 0) AS margen_porcentual,
                   SUM(VENTA_NETA_ASIGNADA_LINEA) /
                       NULLIF(COUNT(DISTINCT SERIE || '-' || CAST(CORRELATIVO AS VARCHAR)), 0) AS ticket_promedio
            FROM V_LINEAS_FACTURADAS_ANALITICAS
            WHERE ANIO BETWEEN ? AND ?
            GROUP BY ANIO
            ORDER BY ANIO
        """
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (start_year, end_year))
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
