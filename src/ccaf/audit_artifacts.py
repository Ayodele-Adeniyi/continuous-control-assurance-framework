"""Audit-trail artifacts for CCAF runs."""

from __future__ import annotations

import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ccaf.config import config_hash, flatten_config


PERIOD_FIELDS = {
    "users": "hire_date",
    "access_grants": "granted_at",
    "auth_logs": "timestamp",
    "changes": "implemented_at",
    "deploy_logs": "deployed_at",
    "log_heartbeats": "last_event_at",
    "ledger": "booked_at",
    "processor_settlement": "settled_at",
}

CONTROL_TOTAL_FIELDS = {
    "ledger": "amount",
    "processor_settlement": "settle_amount",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_input_manifest(data_dir: Path, frames: dict[str, pd.DataFrame],
                         output_path: Path) -> pd.DataFrame:
    rows = []
    for name in sorted(frames):
        path = data_dir / f"{name}.csv"
        rows.append({
            "dataset": name,
            "file": path.name,
            "rows": len(frames[name]),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    manifest = pd.DataFrame(rows)
    manifest.to_csv(output_path, index=False)
    return manifest


def write_calibration_record(config: dict[str, Any], output_path: Path) -> pd.DataFrame:
    rows = []
    for parameter, value in flatten_config(config):
        if parameter == "as_of":
            continue
        rows.append({
            "parameter": parameter,
            "demonstration_value": json.dumps(value) if isinstance(value, list) else value,
            "validation_status": "demonstration default - institution validation required",
            "approved_by": "",
            "approved_at": "",
        })
    record = pd.DataFrame(rows)
    record.to_csv(output_path, index=False)
    return record


def write_source_assurance_record(frames: dict[str, pd.DataFrame],
                                  output_path: Path) -> pd.DataFrame:
    """Record observed extract facts without claiming source completeness."""
    rows = []
    for dataset in sorted(frames):
        frame = frames[dataset]
        period_field = PERIOD_FIELDS.get(dataset, "")
        period_start = ""
        period_end = ""
        if period_field and period_field in frame:
            values = pd.to_datetime(frame[period_field], errors="coerce").dropna()
            if not values.empty:
                period_start = values.min().isoformat()
                period_end = values.max().isoformat()

        control_total_field = CONTROL_TOTAL_FIELDS.get(dataset, "")
        actual_control_total: float | str = ""
        if control_total_field and control_total_field in frame:
            actual_control_total = round(
                float(pd.to_numeric(frame[control_total_field], errors="coerce").sum()), 2
            )

        rows.append({
            "dataset": dataset,
            "source_system": "CCAF seeded synthetic generator",
            "environment": "demonstration",
            "extraction_method": "deterministic local CSV generation",
            "query_or_report_reference": "src/ccaf/generate_data.py",
            "filter_parameters": "fixed synthetic scenario",
            "timezone": "naive demonstration timestamps; production must declare",
            "period_field": period_field,
            "observed_period_start": period_start,
            "observed_period_end": period_end,
            "actual_rows": len(frame),
            "expected_rows": "",
            "row_count_status": "not independently reconciled",
            "control_total_field": control_total_field,
            "actual_control_total": actual_control_total,
            "expected_control_total": "",
            "control_total_status": "not independently reconciled",
            "extract_owner": "",
            "reviewed_by": "",
            "reviewed_at": "",
        })
    record = pd.DataFrame(rows)
    record.to_csv(output_path, index=False)
    return record


def write_run_metadata(config: dict[str, Any], version: str, output_path: Path) -> None:
    metadata = {
        "framework_version": version,
        "run_created_utc": datetime.now(timezone.utc).isoformat(),
        "as_of": config["as_of"],
        "configuration_sha256": config_hash(config),
        "python_version": platform.python_version(),
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
        "risk_statement": (
            "Scores prioritize review within this demonstration; they are not "
            "probabilities of loss or institutionally validated ratings."
        ),
    }
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
