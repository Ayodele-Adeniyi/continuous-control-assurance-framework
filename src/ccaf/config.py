"""Configuration loading for CCAF."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON configuration file and perform basic structural checks."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    required = {
        "as_of",
        "privileged_access",
        "change_logging",
        "reconciliation",
        "scoring",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Configuration is missing sections: {', '.join(missing)}")
    return config


def config_hash(config: dict[str, Any]) -> str:
    """Return a stable SHA-256 hash for the effective configuration."""
    payload = json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def flatten_config(config: dict[str, Any], prefix: str = "") -> list[tuple[str, Any]]:
    """Flatten nested configuration values for the calibration record."""
    rows: list[tuple[str, Any]] = []
    for key, value in config.items():
        name = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            rows.extend(flatten_config(value, name))
        else:
            rows.append((name, value))
    return rows
