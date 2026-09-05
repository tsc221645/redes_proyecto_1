from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import psycopg


def load(input_path: Path, database_url: str) -> int:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    rows = payload["rows"]
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(Path("database/remote_schema.sql").read_text(encoding="utf-8"))
            for row in rows:
                cursor.execute(
                    """INSERT INTO v_lineas_facturadas_analiticas
                    (cliente, nombre_cliente, codigo_pt, descripcion, marca, nombre_marca,
                     linea, pais, moneda, anio, mes, venta_neta_asignada_linea,
                     venta_bruta_linea, costo_estimado_linea, margen_estimado_linea,
                     cantidad_convertida)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (row.get("client_code"), row.get("client_name"), row.get("product_code"),
                     row.get("product_name"), row.get("brand_code"), row.get("brand_name"),
                     row.get("line_code"), row.get("country_code"), row.get("currency"),
                     row.get("year"), row.get("month"), row.get("sales"), row.get("gross_sales"),
                     row.get("cost"), row.get("margin"), row.get("units")),
                )
        connection.commit()
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load an anonymized export into PostgreSQL.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--database-url", default=os.getenv("REMOTE_DATABASE_URL"), required=False)
    args = parser.parse_args()
    if not args.database_url:
        raise SystemExit("Set REMOTE_DATABASE_URL or provide --database-url.")
    print(f"Loaded {load(args.input, args.database_url)} anonymized rows")


if __name__ == "__main__":
    main()
