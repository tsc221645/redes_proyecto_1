from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class SQLAnywhereSettings:
    host: str
    port: int
    server: str
    database: str
    user: str
    password: str
    driver: str
    read_only: bool = True

    @classmethod
    def from_env(cls, env_path: str | Path | None = None) -> "SQLAnywhereSettings":
        load_dotenv(dotenv_path=env_path)
        required = ["SQLANYWHERE_HOST", "SQLANYWHERE_PORT", "SQLANYWHERE_SERVER", "SQLANYWHERE_DATABASE", "SQLANYWHERE_USER", "SQLANYWHERE_PASSWORD", "SQLANYWHERE_DRIVER"]
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise ValueError(f"Missing SQL Anywhere configuration: {', '.join(missing)}")
        return cls(
            host=os.environ["SQLANYWHERE_HOST"],
            port=int(os.environ["SQLANYWHERE_PORT"]),
            server=os.environ["SQLANYWHERE_SERVER"],
            database=os.environ["SQLANYWHERE_DATABASE"],
            user=os.environ["SQLANYWHERE_USER"],
            password=os.environ["SQLANYWHERE_PASSWORD"],
            driver=os.environ["SQLANYWHERE_DRIVER"],
            read_only=os.getenv("SQLANYWHERE_READ_ONLY", "true").lower() == "true",
        )
