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
                                  output_path: Path,
                                  source_metadata: dict[str, Any] | None = None) -> pd.DataFrame:
    """Record observed extract facts without claiming source completeness."""
    rows = []
    defaults = (source_metadata or {}).get("defaults", {})
    dataset_metadata = (source_metadata or {}).get("datasets", {})
    for dataset in sorted(frames):
        frame = frames[dataset]
        supplied = {**defaults, **dataset_metadata.get(dataset, {})}
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

        expected_rows = supplied.get("expected_rows", "")
        if expected_rows in {"", None}:
            row_count_status = "not independently reconciled"
        else:
            row_count_status = (
                "reconciled" if int(expected_rows) == len(frame) else "difference unresolved"
            )

        expected_control_total = supplied.get("expected_control_total", "")
        if expected_control_total in {"", None} or actual_control_total == "":
            control_total_status = "not independently reconciled"
        else:
            difference = abs(float(expected_control_total) - float(actual_control_total))
            control_total_status = "reconciled" if difference <= 0.01 else "difference unresolved"

        demonstration = source_metadata is None
        rows.append({
            "dataset": dataset,
            "source_system": (
                "CCAF seeded synthetic generator" if demonstration
                else supplied.get("source_system", "")
            ),
            "environment": "demonstration" if demonstration else supplied.get("environment", ""),
            "extraction_method": (
                "deterministic local CSV generation" if demonstration
                else supplied.get("extraction_method", "")
            ),
            "query_or_report_reference": (
                "src/ccaf/generate_data.py" if demonstration
                else supplied.get("query_or_report_reference", "")
            ),
            "filter_parameters": (
                "fixed synthetic scenario" if demonstration
                else supplied.get("filter_parameters", "")
            ),
            "timezone": (
                "naive demonstration timestamps; production must declare"
                if demonstration else supplied.get("timezone", "")
            ),
            "period_field": period_field,
            "observed_period_start": period_start,
            "observed_period_end": period_end,
            "actual_rows": len(frame),
            "expected_rows": expected_rows,
            "row_count_status": row_count_status,
            "control_total_field": control_total_field,
            "actual_control_total": actual_control_total,
            "expected_control_total": expected_control_total,
            "control_total_status": control_total_status,
            "extract_owner": supplied.get("extract_owner", ""),
            "reviewed_by": supplied.get("reviewed_by", ""),
            "reviewed_at": supplied.get("reviewed_at", ""),
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
        "review_priority_statement": (
            "Review-priority labels and scores order follow-up within this demonstration; "
            "they are not probabilities of loss, confirmed deficiencies, or "
            "institutionally validated ratings."
        ),
    }
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
