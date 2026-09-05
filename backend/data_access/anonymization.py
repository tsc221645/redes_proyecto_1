from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass
class StableAnonymizer:
    """Deterministically replaces sensitive values while preserving relationships."""

    salt: str
    prefixes: Mapping[str, str] = field(default_factory=lambda: {
        "client": "Cliente",
        "product": "Producto",
        "brand": "Marca",
        "line": "Linea",
        "country": "Pais",
        "invoice": "Factura",
    })

    def anonymize(self, value: Any, kind: str) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        if not normalized:
            return None
        digest = hashlib.sha256(f"{self.salt}:{kind}:{normalized}".encode("utf-8")).hexdigest()
        number = int(digest[:12], 16) % 1_000_000
        return f"{self.prefixes.get(kind, 'Dato')}_{number:06d}"

    def transform_row(self, row: Mapping[str, Any], fields: Mapping[str, str]) -> dict[str, Any]:
        result = dict(row)
        for column, kind in fields.items():
            if column in result:
                result[column] = self.anonymize(result[column], kind)
        return result
