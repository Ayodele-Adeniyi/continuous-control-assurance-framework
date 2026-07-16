"""Module 1 - Privileged Access Monitoring (PA-01 through PA-07)."""

from __future__ import annotations

import pandas as pd

MODULE = "M1 Privileged Access"
RULE_VERSION = "1.3.0"
SOD_CONFLICTS = [
    ("PAYMENT_INITIATE", "PAYMENT_APPROVE"),
    ("DEV_DEPLOY", "PROD_ADMIN"),
    ("GL_POST", "GL_CLOSE"),
]


def _ex(control_id: str, control_name: str, severity: str, entity: str,
        detail: str, exposure: float = 1.0) -> dict:
    return {
        "module": MODULE,
        "control_id": control_id,
        "control_name": control_name,
        "severity": severity,
        "entity_id": entity,
        "detail": detail,
        "exposure_factor": float(exposure),
        "rule_version": RULE_VERSION,
    }


def run(users: pd.DataFrame, grants: pd.DataFrame, auth: pd.DataFrame,
        as_of: pd.Timestamp, config: dict) -> tuple[pd.DataFrame, dict[str, int]]:
    """Execute the seven privileged-access tests and return eligible populations."""
    out: list[dict] = []
    active_grants = grants[grants.grant_status.eq("active")].copy()
    merged = active_grants.merge(users, on="user_id", how="left")
    privileged_grants = merged[merged.privileged.astype(bool)]
    privileged_active = privileged_grants[privileged_grants.status.eq("active")]

    hits = privileged_grants[privileged_grants.status.eq("terminated")]
    for row in hits.itertuples():
        days = (as_of - row.termination_date).days if pd.notna(row.termination_date) else 0
        out.append(_ex(
            "PA-01", "Terminated user with active privileged access", "Critical",
            row.grant_id,
            f"{row.user_id}: {row.entitlement} active {days}d after termination",
            exposure=min(2.0, 1.0 + days / 90),
        ))

    hits = privileged_grants[
        privileged_grants.approved_by.fillna("").str.strip().eq("")
    ]
    for row in hits.itertuples():
        out.append(_ex(
            "PA-02", "Privileged grant without recorded approver", "High",
            row.grant_id, f"{row.user_id}: {row.entitlement} has no approver on record",
        ))

    hits = merged[merged.approved_by.eq(merged.user_id)]
    for row in hits.itertuples():
        out.append(_ex(
            "PA-03", "Self-approved access grant", "High", row.grant_id,
            f"{row.user_id}: {row.entitlement} approved by grantee",
            exposure=1.5 if bool(row.privileged) else 1.0,
        ))

    successful_auth = auth[auth.success.astype(bool)].copy()
    last_login = successful_auth.groupby("user_id")["timestamp"].max()
    dormancy_days = int(config["dormancy_days"])
    for user_id in privileged_active.user_id.unique():
        last = last_login.get(user_id, pd.NaT)
        days = (as_of - last).days if pd.notna(last) else None
        if days is None or days >= dormancy_days:
            detail = "no authentication in analysis window" if days is None else (
                f"last authentication {days}d ago"
            )
            out.append(_ex(
                "PA-04", "Dormant privileged account", "Medium", user_id, detail,
                exposure=1.5 if days is None else 1.2,
            ))

    entitlements_by_user = merged.groupby("user_id")["entitlement"].apply(set)
    for user_id, entitlements in entitlements_by_user.items():
        for first, second in SOD_CONFLICTS:
            if first in entitlements and second in entitlements:
                out.append(_ex(
                    "PA-05", "Segregation-of-duties conflict", "Critical", user_id,
                    f"holds both {first} and {second}", exposure=1.3,
                ))

    temporary = privileged_active[privileged_active.temporary.astype(bool)].copy()
    temporary["expires_at"] = pd.to_datetime(temporary.expires_at, errors="coerce")
    grace_hours = int(config["temporary_access_grace_hours"])
    cutoff = as_of - pd.Timedelta(hours=grace_hours)
    hits = temporary[temporary.expires_at.notna() & temporary.expires_at.lt(cutoff)]
    for row in hits.itertuples():
        overdue_days = max(0, (as_of - row.expires_at).days)
        out.append(_ex(
            "PA-07", "Expired temporary privileged access remains active", "Critical",
            row.grant_id,
            f"{row.user_id}: {row.entitlement} expired {overdue_days}d ago",
            exposure=min(2.0, 1.0 + overdue_days / 30),
        ))

    privileged_users = set(privileged_active.user_id.unique())
    authentication = successful_auth[
        successful_auth.user_id.isin(privileged_users)
    ].copy()
    if not authentication.empty:
        authentication["night"] = authentication.timestamp.dt.hour.isin(
            set(config["night_hours"])
        )
        counts = authentication.groupby("user_id")["night"].sum().reindex(
            sorted(privileged_users), fill_value=0
        )
        median = counts.median()
        mad = (counts - median).abs().median()
        if mad > 0:
            robust_z = 0.6745 * (counts - median) / mad
            threshold = float(config["robust_z_threshold"])
            for user_id, z_value in robust_z[robust_z >= threshold].items():
                out.append(_ex(
                    "PA-06", "Anomalous after-hours privileged authentication", "Medium",
                    user_id,
                    f"{int(counts[user_id])} night logins (robust z={z_value:.1f})",
                    exposure=min(2.0, 1.0 + float(z_value) / 10),
                ))

    populations = {
        "PA-01": len(privileged_grants),
        "PA-02": len(privileged_grants),
        "PA-03": len(merged),
        "PA-04": privileged_active.user_id.nunique(),
        "PA-05": merged.user_id.nunique(),
        "PA-06": len(privileged_users),
        "PA-07": len(temporary),
    }
    return pd.DataFrame(out), populations
