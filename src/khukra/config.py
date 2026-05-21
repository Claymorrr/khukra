"""Runtime configuration from environment."""

from __future__ import annotations

import os
from pathlib import Path


def data_root() -> Path:
    return Path(os.environ.get("KHUKRA_DATA_ROOT", "data"))


def secret_key() -> str:
    return os.environ.get("KHUKRA_SECRET_KEY", "dev-secret-change-in-production")


def cors_origins() -> list[str]:
    raw = os.environ.get(
        "KHUKRA_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [o.strip() for o in raw.split(",") if o.strip()]


def api_port() -> int:
    return int(os.environ.get("KHUKRA_API_PORT", "8000"))


def is_production() -> bool:
    return os.environ.get("KHUKRA_ENV", "development").lower() == "production"
