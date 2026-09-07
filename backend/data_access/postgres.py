from __future__ import annotations

import os
import re
from contextlib import contextmanager
from typing import Any, Iterator


class PostgresRepository:
    """Read-only repository for the anonymized remote analytical dataset."""

    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or os.environ["REMOTE_DATABASE_URL"]

    @contextmanager
    def connect(self) -> Iterator[Any]:
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("psycopg is required for the PostgreSQL remote repository") from exc
        connection = psycopg.connect(self.database_url, autocommit=True)
        try:
            # Defense in depth: analytical MCP connections cannot write even if
            # the configured database role has more privileges than intended.
            with connection.cursor() as cursor:
                cursor.execute("SET default_transaction_read_only = on")
            yield connection
        finally:
            connection.close()

    def query(self, sql: str, parameters: tuple[Any, ...]) -> list[dict[str, Any]]:
        # Business SQL is repository-owned. This adapter translates the small
        # SQL Anywhere subset used by the tools to PostgreSQL placeholders and LIMIT.
        sql, parameters = self._translate(sql, parameters)
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, parameters)
                columns = [item.name for item in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def _translate(sql: str, parameters: tuple[Any, ...]) -> tuple[str, tuple[Any, ...]]:
        limit_value: Any | None = None
        top_param = re.search(r"\bSELECT\s+TOP\s+\?\s+", sql, re.IGNORECASE)
        if top_param:
            limit_value = parameters[0]
            parameters = parameters[1:]
            sql = sql[:top_param.start()] + "SELECT " + sql[top_param.end():]
        else:
            top_fixed = re.search(r"\bSELECT\s+TOP\s+(\d+)\s+", sql, re.IGNORECASE)
            if top_fixed:
                limit_value = int(top_fixed.group(1))
                sql = sql[:top_fixed.start()] + "SELECT " + sql[top_fixed.end():]
        sql = sql.replace("?", "%s")
        if limit_value is not None:
            sql = sql.rstrip().rstrip(";") + " LIMIT %s"
            parameters = (*parameters, limit_value)
        return sql, parameters
