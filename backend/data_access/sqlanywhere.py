from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from .config import SQLAnywhereSettings


class SQLAnywhereConnection:
    """Small ODBC gateway for SQL Anywhere; credentials never enter logs."""

    def __init__(self, settings: SQLAnywhereSettings) -> None:
        self.settings = settings

    def connection_string(self) -> str:
        """Build the ODBC connection string for the local TCP server."""
        read_only = ";ReadOnly=YES" if self.settings.read_only else ""
        return (
            f"DRIVER={{{self.settings.driver}}};"
            f"Host={self.settings.host}:{self.settings.port};"
            f"ServerName={self.settings.server};"
            f"DBN={self.settings.database};"
            f"UID={self.settings.user};PWD={self.settings.password}{read_only}"
        )

    @contextmanager
    def connect(self) -> Iterator[Any]:
        """Open and close an ODBC connection."""
        try:
            import pyodbc
        except ImportError as exc:
            raise RuntimeError("pyodbc is required for SQL Anywhere access") from exc
        connection = pyodbc.connect(self.connection_string(), autocommit=True)
        try:
            yield connection
        finally:
            connection.close()
