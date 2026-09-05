from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path

from backend.data_access.anonymization import StableAnonymizer
from backend.data_access.config import SQLAnywhereSettings
from backend.data_access.repositories import SalesRepository
from backend.data_access.sqlanywhere import SQLAnywhereConnection


APPROVED_FIELDS = {
    "client_code": "client",
    "client_name": "client",
    "product_code": "product",
    "product_name": "product",
    "brand_code": "brand",
    "brand_name": "brand",
    "line_code": "line",
    "country_code": "country",
    "currency": None,
    "year": None,
    "month": None,
    "sales": None,
    "gross_sales": None,
    "cost": None,
    "margin": None,
    "units": None,
}


def export(start_date: str, end_date: str, output: Path, salt: str) -> int:
    query = """
        SELECT v.CLIENTE AS client_code,
               pc.NOMBRE_CLIENTE AS client_name,
               v.CODIGO_PT AS product_code,
               v.DESCRIPCION AS product_name,
               v.MARCA AS brand_code,
               pm.NOMBRE AS brand_name,
               v.LINEA AS line_code,
               v.PAIS AS country_code,
               v.MONEDA AS currency,
               v.ANIO AS year,
               v.MES AS month,
               SUM(v.VENTA_NETA_ASIGNADA_LINEA) AS sales,
               SUM(v.VENTA_BRUTA_LINEA) AS gross_sales,
               SUM(v.COSTO_ESTIMADO_LINEA) AS cost,
               SUM(v.MARGEN_ESTIMADO_LINEA) AS margin,
               SUM(v.CANTIDAD_CONVERTIDA) AS units
        FROM V_LINEAS_FACTURADAS_ANALITICAS v
        LEFT JOIN PT_MARCAS pm ON v.MARCA = pm.MARCA
        LEFT JOIN PT_CLIENTES pc ON v.CLIENTE = pc.CLIENTE
        WHERE v.FECHA_INGRESO BETWEEN ? AND ?
        GROUP BY v.CLIENTE, pc.NOMBRE_CLIENTE, v.CODIGO_PT, v.DESCRIPCION,
                 v.MARCA, pm.NOMBRE, v.LINEA, v.PAIS, v.MONEDA, v.ANIO, v.MES
        ORDER BY v.ANIO, v.MES
    """
    settings = SQLAnywhereSettings.from_env()
    rows = SalesRepository(SQLAnywhereConnection(settings)).query(query, (start_date, end_date))
    anonymizer = StableAnonymizer(salt)
    transformed = [anonymizer.transform_row(row, {key: kind for key, kind in APPROVED_FIELDS.items() if kind}) for row in rows]
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "generated_at": date.today().isoformat(),
            "start_date": start_date,
            "end_date": end_date,
            "row_count": len(transformed),
            "source": "approved analytical read model",
        },
        "rows": transformed,
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return len(transformed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export approved SQL Anywhere metrics with stable anonymization.")
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--salt", default=os.getenv("ANONYMIZATION_SALT"))
    args = parser.parse_args()
    if not args.salt:
        raise SystemExit("Set ANONYMIZATION_SALT or provide --salt.")
    count = export(args.start_date, args.end_date, args.output, args.salt)
    print(f"Exported {count} anonymized aggregate rows to {args.output}")


if __name__ == "__main__":
    main()
