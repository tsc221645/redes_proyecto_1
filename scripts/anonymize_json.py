from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from backend.data_access.anonymization import StableAnonymizer


FIELDS = {
    "CLIENTE": "client",
    "NOMBRE_CLIENTE": "client",
    "CODIGO_PT": "product",
    "PRODUCTO": "product",
    "MARCA": "brand",
    "NOMBRE_MARCA": "brand",
    "LINEA": "line",
    "NOMBRE_LINEA": "line",
    "PAIS": "country",
    "FACTURA": "invoice",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Anonymize a JSON array without changing relationships.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--salt", default=os.getenv("ANONYMIZATION_SALT"), help="Stable secret salt.")
    args = parser.parse_args()
    if not args.salt:
        raise SystemExit("Set ANONYMIZATION_SALT or provide --salt.")
    rows = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise SystemExit("Input must be a JSON array of objects.")
    anonymizer = StableAnonymizer(args.salt)
    output = [anonymizer.transform_row(row, FIELDS) for row in rows]
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
