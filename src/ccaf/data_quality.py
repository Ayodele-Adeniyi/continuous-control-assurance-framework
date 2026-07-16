"""Source-data validation for CCAF runs."""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd


FINDING_COLUMNS = ["severity", "check_id", "dataset", "field", "affected_rows", "detail"]

REQUIRED_COLUMNS = {
    "users": {"user_id", "status", "hire_date", "termination_date"},
    "access_grants": {
        "grant_id", "user_id", "entitlement", "privileged", "granted_at",
        "approved_by", "grant_status", "temporary", "expires_at",
    },
    "auth_logs": {"event_id", "user_id", "timestamp", "success"},
    "changes": {
        "change_id", "system", "approved_by", "implemented_by", "approved_at",
        "implemented_at", "emergency", "pir_completed", "test_completed",
        "test_approved_by",
    },
    "deploy_logs": {"deploy_id", "system", "deployed_at", "change_id"},
    "log_heartbeats": {"source_id", "system", "log_source", "last_event_at"},
    "ledger": {
        "ledger_row_id", "txn_id", "account_id", "amount", "booked_at", "reconciled",
    },
    "processor_settlement": {
        "settlement_row_id", "txn_id", "settle_amount", "settled_at",
    },
}

OPTIONAL_COLUMNS = {
    "ground_truth": {"injection_id", "control_id", "entity_id", "description"},
}

PRIMARY_KEYS = {
    "users": "user_id",
    "access_grants": "grant_id",
    "auth_logs": "event_id",
    "changes": "change_id",
    "deploy_logs": "deploy_id",
    "log_heartbeats": "source_id",
    "ledger": "ledger_row_id",
    "processor_settlement": "settlement_row_id",
    "ground_truth": "injection_id",
}

REQUIRED_TIMESTAMPS = {
    "users": ["hire_date"],
    "access_grants": ["granted_at"],
    "auth_logs": ["timestamp"],
    "changes": ["implemented_at"],
    "deploy_logs": ["deployed_at"],
    "log_heartbeats": ["last_event_at"],
    "ledger": ["booked_at"],
    "processor_settlement": ["settled_at"],
}

BOOLEAN_FIELDS = {
    "access_grants": ["privileged", "temporary"],
    "auth_logs": ["success"],
    "changes": ["emergency", "pir_completed", "test_completed"],
    "ledger": ["reconciled"],
}


def _finding(severity: str, check_id: str, dataset: str, field: str,
             affected_rows: int, detail: str) -> dict:
    return {
        "severity": severity,
        "check_id": check_id,
        "dataset": dataset,
        "field": field,
        "affected_rows": int(affected_rows),
        "detail": detail,
    }


def validate_frames(frames: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Validate schemas, keys, timestamps, and selected referential relationships."""
    findings: list[dict] = []

    columns_to_validate = dict(REQUIRED_COLUMNS)
    for dataset, required in OPTIONAL_COLUMNS.items():
        if dataset in frames:
            columns_to_validate[dataset] = required

    for dataset, required in columns_to_validate.items():
        if dataset not in frames:
            findings.append(_finding(
                "Critical", "DQ-001", dataset, "", 1, "Required dataset is missing"
            ))
            continue

        frame = frames[dataset]
        if frame.empty:
            findings.append(_finding(
                "Critical", "DQ-009", dataset, "", 1,
                "Required dataset contains no rows",
            ))
        missing = sorted(required - set(frame.columns))
        if missing:
            findings.append(_finding(
                "Critical", "DQ-002", dataset, ", ".join(missing), len(missing),
                "Required columns are missing",
            ))
            continue

        key = PRIMARY_KEYS[dataset]
        null_keys = int(frame[key].isna().sum() + frame[key].astype(str).str.strip().eq("").sum())
        if null_keys:
            findings.append(_finding(
                "Critical", "DQ-003", dataset, key, null_keys, "Primary key is blank"
            ))
        duplicate_keys = int(frame[key].duplicated(keep=False).sum())
        if duplicate_keys:
            findings.append(_finding(
                "Critical", "DQ-004", dataset, key, duplicate_keys,
                "Primary key is not unique",
            ))

        for field in REQUIRED_TIMESTAMPS.get(dataset, []):
            invalid = int(pd.to_datetime(frame[field], errors="coerce").isna().sum())
            if invalid:
                findings.append(_finding(
                    "High", "DQ-005", dataset, field, invalid,
                    "Required timestamp is missing or cannot be parsed",
                ))

        for field in BOOLEAN_FIELDS.get(dataset, []):
            raw = frame[field]
            normalized = raw.dropna().astype(str).str.strip().str.lower()
            invalid = int(raw.isna().sum()) + int(
                (~normalized.isin({"true", "false", "1", "0"})).sum()
            )
            if invalid:
                findings.append(_finding(
                    "High", "DQ-010", dataset, field, invalid,
                    "Boolean field is missing or contains an unsupported value",
                ))

    if "users" in frames and "access_grants" in frames:
        known = set(frames["users"].get("user_id", pd.Series(dtype=str)).dropna())
        grants = frames["access_grants"]
        if "user_id" in grants:
            orphan = int((~grants["user_id"].isin(known)).sum())
            if orphan:
                findings.append(_finding(
                    "High", "DQ-006", "access_grants", "user_id", orphan,
                    "Grant refers to a user absent from the user roster",
                ))

    if "users" in frames and "auth_logs" in frames:
        known = set(frames["users"].get("user_id", pd.Series(dtype=str)).dropna())
        auth = frames["auth_logs"]
        if "user_id" in auth:
            orphan = int((~auth["user_id"].isin(known)).sum())
            if orphan:
                findings.append(_finding(
                    "High", "DQ-007", "auth_logs", "user_id", orphan,
                    "Authentication event refers to a user absent from the user roster",
                ))

    if "users" in frames:
        users = frames["users"]
        if {"status", "termination_date"}.issubset(users.columns):
            terminated = users["status"].eq("terminated")
            missing_term = int((terminated & pd.to_datetime(
                users["termination_date"], errors="coerce"
            ).isna()).sum())
            if missing_term:
                findings.append(_finding(
                    "High", "DQ-008", "users", "termination_date", missing_term,
                    "Terminated user lacks a termination date",
                ))

    if "access_grants" in frames:
        grants = frames["access_grants"]
        needed = {"temporary", "expires_at", "grant_status"}
        if needed.issubset(grants.columns):
            temporary_active = (
                grants["temporary"].astype(bool)
                & grants["grant_status"].eq("active")
            )
            missing_expiry = int((
                temporary_active
                & pd.to_datetime(grants["expires_at"], errors="coerce").isna()
            ).sum())
            if missing_expiry:
                findings.append(_finding(
                    "High", "DQ-011", "access_grants", "expires_at", missing_expiry,
                    "Active temporary grant lacks a valid expiry timestamp",
                ))

    if "changes" in frames:
        changes = frames["changes"]
        if {"approved_at", "implemented_at"}.issubset(changes.columns):
            approved = pd.to_datetime(changes["approved_at"], errors="coerce")
            implemented = pd.to_datetime(changes["implemented_at"], errors="coerce")
            after_implementation = int((
                approved.notna() & implemented.notna() & approved.gt(implemented)
            ).sum())
            if after_implementation:
                findings.append(_finding(
                    "High", "DQ-012", "changes", "approved_at", after_implementation,
                    "Recorded approval occurs after implementation",
                ))

    return pd.DataFrame(findings, columns=FINDING_COLUMNS)


def has_blocking_findings(findings: pd.DataFrame) -> bool:
    """Return True when Critical or High findings make analytics unreliable."""
    if findings.empty:
        return False
    return findings["severity"].isin({"Critical", "High"}).any()


def normalize_boolean_fields(
    frames: Mapping[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Return copies with supported boolean representations normalized."""
    normalized_frames = dict(frames)
    mapping = {"true": True, "1": True, "false": False, "0": False}
    for dataset, fields in BOOLEAN_FIELDS.items():
        if dataset not in frames:
            continue
        frame = frames[dataset].copy()
        for field in fields:
            if field not in frame:
                continue
            values = frame[field].astype(str).str.strip().str.lower().map(mapping)
            if values.isna().any():
                raise ValueError(
                    f"Cannot normalize {dataset}.{field}; run data-quality validation first"
                )
            frame[field] = values.astype(bool)
        normalized_frames[dataset] = frame
    return normalized_frames
