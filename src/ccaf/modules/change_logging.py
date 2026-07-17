"""Module 2 - Change Management and Logging Integrity."""

from __future__ import annotations

import pandas as pd

from ccaf.results import COMPLETED, NOT_EVALUABLE, evaluation, exception_frame

MODULE = "M2 Change & Logging"
RULE_VERSION = "1.3.1"


def _ex(control_id: str, control_name: str, review_priority: str, entity: str,
        detail: str, exposure: float = 1.0) -> dict:
    return {
        "module": MODULE,
        "control_id": control_id,
        "control_name": control_name,
        "review_priority": review_priority,
        "entity_id": entity,
        "detail": detail,
        "exposure_factor": float(exposure),
        "rule_version": RULE_VERSION,
    }


def run(changes: pd.DataFrame, deploys: pd.DataFrame, heartbeats: pd.DataFrame,
        as_of: pd.Timestamp, config: dict) -> tuple[pd.DataFrame, dict[str, dict]]:
    out: list[dict] = []

    hits = changes[
        changes.approved_by.fillna("").str.strip().eq("")
        | changes.approved_at.isna()
    ]
    for row in hits.itertuples():
        missing = []
        if pd.isna(row.approved_by) or not str(row.approved_by).strip():
            missing.append("approver")
        if pd.isna(row.approved_at):
            missing.append("approval timestamp")
        out.append(_ex(
            "CM-01", "Change implemented without recorded approval", "High",
            row.change_id,
            f"{row.system} {row.category} change lacks recorded {' and '.join(missing)}",
            exposure=1.4 if row.category == "major" else 1.0,
        ))

    hits = changes[
        changes.approved_by.fillna("").str.strip().ne("")
        & changes.approved_by.eq(changes.implemented_by)
    ]
    for row in hits.itertuples():
        out.append(_ex(
            "CM-02", "Approver and implementer are the same individual", "High",
            row.change_id, f"{row.approved_by} approved and implemented on {row.system}",
        ))

    hits = changes[
        changes.emergency.astype(bool) & ~changes.pir_completed.astype(bool)
    ]
    for row in hits.itertuples():
        out.append(_ex(
            "CM-03", "Emergency change without post-implementation review", "Medium",
            row.change_id, f"emergency change on {row.system}; no review recorded",
        ))

    valid_changes = set(changes.change_id)
    deployment = deploys.copy()
    deployment["change_id"] = deployment.change_id.fillna("")
    hits = deployment[
        deployment.change_id.str.strip().eq("")
        | ~deployment.change_id.isin(valid_changes)
    ]
    for row in hits.itertuples():
        reason = "no change reference" if not row.change_id.strip() else (
            f"unknown change {row.change_id}"
        )
        out.append(_ex(
            "CM-04", "Deployment without matching change record", "Critical",
            row.deploy_id, f"{row.system} deployment references {reason}",
        ))

    heartbeat = heartbeats.copy()
    heartbeat["hours_quiet"] = (
        as_of - heartbeat.last_event_at
    ).dt.total_seconds() / 3600
    hits = heartbeat[heartbeat.hours_quiet >= float(config["heartbeat_hours"])]
    for row in hits.itertuples():
        out.append(_ex(
            "CM-05", "Silent log source", "High", row.source_id,
            f"{row.system}/{row.log_source} quiet {row.hours_quiet:.0f}h",
            exposure=min(2.0, 1.0 + row.hours_quiet / 96),
        ))

    recent_days = int(config["recent_window_days"])
    recent = changes[
        changes.implemented_at >= as_of - pd.Timedelta(days=recent_days)
    ]
    baseline = changes[
        changes.implemented_at < as_of - pd.Timedelta(days=recent_days)
    ]
    minimum_recent = int(config["minimum_recent_changes"])
    minimum_baseline = int(config["minimum_baseline_changes"])
    cm06_status = COMPLETED
    cm06_reason = ""
    if len(recent) < minimum_recent or len(baseline) < minimum_baseline:
        cm06_status = NOT_EVALUABLE
        cm06_reason = (
            f"requires at least {minimum_recent} recent and {minimum_baseline} baseline "
            f"changes; supplied {len(recent)} and {len(baseline)}"
        )
    elif int(baseline.emergency.astype(bool).sum()) == 0:
        cm06_status = NOT_EVALUABLE
        cm06_reason = "baseline period contains no emergency changes for a stable rate comparison"
    else:
        recent_rate = recent.emergency.mean()
        baseline_rate = baseline.emergency.mean()
        ratio = recent_rate / baseline_rate
        if ratio >= float(config["emergency_spike_factor"]):
            out.append(_ex(
                "CM-06", "Emergency-change rate spike", "Medium", "portfolio",
                f"emergency rate {recent_rate:.0%} vs baseline {baseline_rate:.0%} "
                f"({ratio:.1f}x)", exposure=min(2.0, ratio / 2),
            ))

    test_approver = changes.test_approved_by.fillna("").str.strip()
    hits = changes[~changes.test_completed.astype(bool) | test_approver.eq("")]
    for row in hits.itertuples():
        reason = (
            "no completed preproduction test recorded"
            if not bool(row.test_completed)
            else "test completed but no test approval recorded"
        )
        out.append(_ex(
            "CM-07", "Implemented change lacks recorded preproduction testing", "High",
            row.change_id, f"{row.system} {row.category} change: {reason}",
            exposure=1.4 if row.category == "major" else 1.0,
        ))

    evaluations = {
        "CM-01": evaluation("Change implemented without recorded approval", "High", len(changes)),
        "CM-02": evaluation("Approver and implementer are the same individual", "High", len(changes)),
        "CM-03": evaluation(
            "Emergency change without post-implementation review", "Medium",
            int(changes.emergency.astype(bool).sum()),
        ),
        "CM-04": evaluation("Deployment without matching change record", "Critical", len(deploys)),
        "CM-05": evaluation("Silent log source", "High", len(heartbeats)),
        "CM-06": evaluation(
            "Emergency-change rate spike", "Medium", 1, cm06_status, cm06_reason
        ),
        "CM-07": evaluation(
            "Implemented change lacks recorded preproduction testing", "High", len(changes)
        ),
    }
    return exception_frame(out), evaluations
