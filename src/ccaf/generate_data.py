"""Seeded synthetic data and ground-truth generator for CCAF."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_SEED = 42
MIN_SEED = 0
MAX_SEED = (1 << 32) - 1
# Retained for compatibility with existing imports and the fixed release benchmark.
SEED = DEFAULT_SEED
AS_OF = pd.Timestamp("2026-07-01 00:00:00")
WINDOW_DAYS = 90

FIRST = [
    "Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie",
    "Avery", "Quinn", "Drew", "Reese", "Parker", "Rowan", "Skyler", "Emerson",
]
LAST = [
    "Okafor", "Nguyen", "Garcia", "Smith", "Johnson", "Lee", "Patel", "Brown",
    "Martinez", "Kim", "Davis", "Lopez", "Chen", "Walker", "Adebayo", "Hughes",
]
DEPTS = [
    "Payments Ops", "Core Banking", "IT Operations", "Engineering", "Finance",
    "Risk & Compliance", "Customer Service", "Security",
]
SYSTEMS = [
    "core-banking", "payments-gateway", "card-switch", "gl-system", "crm",
    "data-warehouse",
]
ENTITLEMENTS = [
    ("ENT-001", "CORE_VIEW", False), ("ENT-002", "CORE_TELLER", False),
    ("ENT-003", "PROD_ADMIN", True), ("ENT-004", "DB_ADMIN", True),
    ("ENT-005", "DEV_DEPLOY", True), ("ENT-006", "PAYMENT_INITIATE", False),
    ("ENT-007", "PAYMENT_APPROVE", True), ("ENT-008", "GL_POST", False),
    ("ENT-009", "GL_CLOSE", True), ("ENT-010", "USER_ADMIN", True),
    ("ENT-011", "REPORT_VIEW", False), ("ENT-012", "CRM_AGENT", False),
    ("ENT-013", "SEC_CONFIG", True), ("ENT-014", "DWH_QUERY", False),
]
SOD_CONFLICTS = [
    ("PAYMENT_INITIATE", "PAYMENT_APPROVE"),
    ("DEV_DEPLOY", "PROD_ADMIN"),
    ("GL_POST", "GL_CLOSE"),
]


def validate_seed(seed: int) -> int:
    """Return a validated synthetic seed suitable for NumPy and pandas."""
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise TypeError("The synthetic seed must be an integer")
    value = int(seed)
    if not MIN_SEED <= value <= MAX_SEED:
        raise ValueError(
            f"The synthetic seed must be between {MIN_SEED} and {MAX_SEED}"
        )
    return value


def _rng(seed: int = DEFAULT_SEED) -> np.random.Generator:
    return np.random.default_rng(validate_seed(seed))


def _sample_state(seed: int, legacy_state: int) -> int:
    """Derive an independent pandas sample state without changing seed 42 outputs."""
    seed = validate_seed(seed)
    if seed == DEFAULT_SEED:
        return legacy_state
    return int(
        np.random.SeedSequence([seed, legacy_state]).generate_state(
            1, dtype=np.uint32
        )[0]
    )


def _truth(rows: list[dict], control_id: str, entity_id: str, description: str) -> None:
    rows.append({
        "injection_id": f"GT-{len(rows) + 1:04d}",
        "control_id": control_id,
        "entity_id": str(entity_id),
        "description": description,
    })


def make_users(rng: np.random.Generator, n: int = 300) -> pd.DataFrame:
    ids = [f"U{i:04d}" for i in range(1, n + 1)]
    status = np.where(rng.random(n) < 0.08, "terminated", "active")
    termination = [
        AS_OF - pd.Timedelta(days=int(days)) if state == "terminated" else pd.NaT
        for state, days in zip(status, rng.integers(5, 200, n))
    ]
    return pd.DataFrame({
        "user_id": ids,
        "name": [f"{rng.choice(FIRST)} {rng.choice(LAST)}" for _ in ids],
        "department": rng.choice(DEPTS, n),
        "hire_date": (AS_OF - pd.to_timedelta(rng.integers(120, 3000, n), unit="D")).normalize(),
        "status": status,
        "termination_date": pd.to_datetime(termination),
    })


def make_grants(rng: np.random.Generator, users: pd.DataFrame,
                truth: list[dict], seed: int = DEFAULT_SEED) -> pd.DataFrame:
    entitlements = pd.DataFrame(
        ENTITLEMENTS, columns=["entitlement_id", "entitlement", "privileged"]
    )
    managers = users.sample(
        30, random_state=_sample_state(seed, SEED)
    )["user_id"].tolist()
    rows: list[dict] = []
    grant_number = 1

    for user in users.itertuples():
        picks = entitlements.sample(
            int(rng.integers(1, 5)), random_state=int(rng.integers(0, 1 << 31))
        )
        for entitlement in picks.itertuples():
            rows.append({
                "grant_id": f"G{grant_number:05d}",
                "user_id": user.user_id,
                "entitlement": entitlement.entitlement,
                "privileged": bool(entitlement.privileged),
                "granted_at": AS_OF - pd.Timedelta(days=int(rng.integers(10, 900))),
                "approved_by": str(rng.choice(managers)),
                "grant_status": "active",
                "temporary": False,
                "expires_at": pd.NaT,
            })
            grant_number += 1
    grants = pd.DataFrame(rows)

    # Remove naturally occurring toxic pairs so the seeded SoD population is known.
    for first, second in SOD_CONFLICTS:
        with_first = set(grants.loc[grants.entitlement == first, "user_id"])
        grants = grants.drop(
            grants[(grants.entitlement == second) & grants.user_id.isin(with_first)].index
        )
    grants = grants.reset_index(drop=True)

    terminated = set(users.loc[users.status == "terminated", "user_id"])
    grants.loc[grants.user_id.isin(terminated), "grant_status"] = "revoked"
    candidates = grants[(grants.user_id.isin(terminated)) & grants.privileged]
    candidates = candidates.drop_duplicates("user_id").sample(
        min(6, candidates.user_id.nunique()), random_state=_sample_state(seed, 12)
    )
    grants.loc[candidates.index, "grant_status"] = "active"
    for row in grants.loc[candidates.index].itertuples():
        _truth(truth, "PA-01", row.grant_id,
               "Terminated user retained an active privileged grant")

    active_privileged = grants[
        grants.privileged & grants.grant_status.eq("active")
    ].drop(index=candidates.index, errors="ignore")
    missing_approval = active_privileged.sample(
        8, random_state=_sample_state(seed, 1)
    )
    grants.loc[missing_approval.index, "approved_by"] = ""
    for row in grants.loc[missing_approval.index].itertuples():
        _truth(truth, "PA-02", row.grant_id,
               "Privileged grant has no recorded approver")

    self_candidates = grants[
        grants.grant_status.eq("active") & ~grants.index.isin(missing_approval.index)
    ]
    self_approved = self_candidates.sample(
        5, random_state=_sample_state(seed, 2)
    )
    grants.loc[self_approved.index, "approved_by"] = grants.loc[
        self_approved.index, "user_id"
    ]
    for row in grants.loc[self_approved.index].itertuples():
        _truth(truth, "PA-03", row.grant_id, "Access grant was self-approved")

    active_users = sorted(users.loc[users.status == "active", "user_id"])
    conflicted = rng.choice(active_users, 7, replace=False)
    for index, user_id in enumerate(conflicted):
        first, second = SOD_CONFLICTS[index % len(SOD_CONFLICTS)]
        for entitlement_name in (first, second):
            already = grants[
                grants.user_id.eq(user_id) & grants.entitlement.eq(entitlement_name)
            ]
            if not already.empty:
                grants.loc[already.index, "grant_status"] = "active"
                continue
            privileged = bool(
                entitlements.loc[
                    entitlements.entitlement == entitlement_name, "privileged"
                ].iloc[0]
            )
            grants = pd.concat([grants, pd.DataFrame([{
                "grant_id": f"G{grant_number:05d}",
                "user_id": user_id,
                "entitlement": entitlement_name,
                "privileged": privileged,
                "granted_at": AS_OF - pd.Timedelta(days=int(rng.integers(30, 400))),
                "approved_by": str(rng.choice(managers)),
                "grant_status": "active",
                "temporary": False,
                "expires_at": pd.NaT,
            }])], ignore_index=True)
            grant_number += 1
        _truth(truth, "PA-05", user_id, "User holds a seeded toxic entitlement pair")

    active_user_ids = set(users.loc[users.status == "active", "user_id"])
    temporary = grants[
        grants.user_id.isin(active_user_ids)
        & grants.privileged
        & grants.grant_status.eq("active")
    ].sample(9, random_state=_sample_state(seed, 13))
    grants.loc[temporary.index, "temporary"] = True
    expired = temporary.iloc[:4]
    current = temporary.iloc[4:]
    grants.loc[expired.index, "expires_at"] = [
        AS_OF - pd.Timedelta(days=day) for day in (2, 7, 14, 30)
    ]
    grants.loc[current.index, "expires_at"] = [
        AS_OF + pd.Timedelta(days=day) for day in (2, 7, 14, 30, 60)
    ]
    for row in grants.loc[expired.index].itertuples():
        _truth(
            truth, "PA-07", row.grant_id,
            "Temporary privileged grant remained active after its expiry",
        )

    return grants.drop_duplicates(subset=["user_id", "entitlement"], keep="first")


def make_auth_logs(rng: np.random.Generator, users: pd.DataFrame,
                   grants: pd.DataFrame, truth: list[dict]) -> pd.DataFrame:
    active = users.loc[users.status == "active", "user_id"].tolist()
    privileged_users = grants.loc[
        grants.privileged & grants.grant_status.eq("active"), "user_id"
    ].unique().tolist()
    dormant = rng.choice(
        [user for user in privileged_users if user in active], 6, replace=False
    ).tolist()
    for user_id in dormant:
        _truth(truth, "PA-04", user_id, "Privileged user has no authentication in the window")

    rows: list[dict] = []
    event_number = 1
    for user_id in active:
        if user_id in dormant:
            continue
        weekly_rate = 1.6 if user_id in privileged_users else 0.7
        count = rng.poisson(weekly_rate * WINDOW_DAYS / 7 * 5)
        for _ in range(int(count)):
            timestamp = (
                AS_OF - pd.Timedelta(days=int(rng.integers(0, WINDOW_DAYS)))
                + pd.Timedelta(
                    hours=int(np.clip(rng.normal(13, 3.2), 0, 23)),
                    minutes=int(rng.integers(0, 60)),
                )
            )
            rows.append({
                "event_id": f"L{event_number:06d}",
                "user_id": user_id,
                "system": str(rng.choice(SYSTEMS)),
                "timestamp": timestamp,
                "success": bool(rng.random() > 0.03),
            })
            event_number += 1

    night_users = rng.choice(
        [user for user in privileged_users if user in active and user not in dormant],
        3, replace=False,
    )
    for user_id in night_users:
        for _ in range(14):
            timestamp = (
                AS_OF - pd.Timedelta(days=int(rng.integers(0, 21)))
                + pd.Timedelta(
                    hours=int(rng.choice([23, 0, 1, 2, 3])),
                    minutes=int(rng.integers(0, 60)),
                )
            )
            rows.append({
                "event_id": f"L{event_number:06d}",
                "user_id": user_id,
                "system": "core-banking",
                "timestamp": timestamp,
                "success": True,
            })
            event_number += 1
        _truth(truth, "PA-06", user_id, "Privileged user has a seeded night-login burst")
    return pd.DataFrame(rows)


def make_changes(rng: np.random.Generator, users: pd.DataFrame,
                 truth: list[dict], seed: int = DEFAULT_SEED) -> pd.DataFrame:
    staff = users.loc[users.status == "active", "user_id"].tolist()
    rows = []
    for number in range(1, 401):
        requester, approver, implementer = rng.choice(staff, 3, replace=False)
        implemented_at = AS_OF - pd.Timedelta(
            days=int(rng.integers(0, WINDOW_DAYS)), hours=int(rng.integers(0, 24))
        )
        emergency = bool(rng.random() < 0.10)
        rows.append({
            "change_id": f"CHG{number:05d}",
            "system": str(rng.choice(SYSTEMS)),
            "category": str(rng.choice(["standard", "normal", "major"])),
            "requested_by": requester,
            "approved_by": approver,
            "implemented_by": implementer,
            "approved_at": implemented_at - pd.Timedelta(hours=int(rng.integers(4, 96))),
            "implemented_at": implemented_at,
            "emergency": emergency,
            "pir_completed": emergency,
            "test_completed": True,
            "test_approved_by": approver,
            "status": "closed",
        })
    changes = pd.DataFrame(rows)

    no_approval = changes.sample(12, random_state=_sample_state(seed, 3))
    changes.loc[no_approval.index, ["approved_by", "approved_at"]] = ["", pd.NaT]
    for row in changes.loc[no_approval.index].itertuples():
        _truth(truth, "CM-01", row.change_id, "Implemented change lacks approval")

    same_person = changes.drop(no_approval.index).sample(
        9, random_state=_sample_state(seed, 4)
    )
    changes.loc[same_person.index, "approved_by"] = changes.loc[
        same_person.index, "implemented_by"
    ]
    for row in changes.loc[same_person.index].itertuples():
        _truth(truth, "CM-02", row.change_id, "Approver also implemented the change")

    untested = changes.drop(no_approval.index.union(same_person.index)).sample(
        6, random_state=_sample_state(seed, 14)
    )
    changes.loc[untested.index, "test_completed"] = False
    changes.loc[untested.index, "test_approved_by"] = ""
    for row in changes.loc[untested.index].itertuples():
        _truth(
            truth, "CM-07", row.change_id,
            "Implemented change lacks recorded preproduction test evidence",
        )

    recent = changes[
        changes.implemented_at >= AS_OF - pd.Timedelta(days=14)
    ].sample(18, random_state=_sample_state(seed, 6))
    changes.loc[recent.index, ["emergency", "pir_completed"]] = [True, True]
    no_review = changes[changes.emergency].sample(
        7, random_state=_sample_state(seed, 5)
    )
    changes.loc[no_review.index, "pir_completed"] = False
    for row in changes.loc[no_review.index].itertuples():
        _truth(truth, "CM-03", row.change_id, "Emergency change lacks post-implementation review")
    _truth(truth, "CM-06", "portfolio", "Recent emergency-change rate exceeds baseline")
    return changes


def make_deploy_logs(rng: np.random.Generator, changes: pd.DataFrame,
                     truth: list[dict]) -> pd.DataFrame:
    rows = []
    for number, change in enumerate(changes.itertuples(), start=1):
        if rng.random() < 0.9:
            rows.append({
                "deploy_id": f"D{number:05d}",
                "system": change.system,
                "deployed_at": change.implemented_at,
                "change_id": change.change_id,
            })
    for number in range(10):
        deploy_id = f"DX{number:03d}"
        rows.append({
            "deploy_id": deploy_id,
            "system": str(rng.choice(SYSTEMS)),
            "deployed_at": AS_OF - pd.Timedelta(days=int(rng.integers(0, WINDOW_DAYS))),
            "change_id": "" if number % 2 == 0 else f"CHG9{number:04d}",
        })
        _truth(truth, "CM-04", deploy_id, "Deployment has no valid change record")
    return pd.DataFrame(rows)


def make_log_heartbeats(rng: np.random.Generator, truth: list[dict],
                        seed: int = DEFAULT_SEED) -> pd.DataFrame:
    rows = []
    for number, (system, source) in enumerate(
        (pair for system in SYSTEMS for pair in [(system, item) for item in ("app", "db", "os", "security")])
    ):
        rows.append({
            "source_id": f"SRC{number:03d}",
            "system": system,
            "log_source": source,
            "last_event_at": AS_OF - pd.Timedelta(hours=float(rng.uniform(0.2, 8))),
        })
    heartbeats = pd.DataFrame(rows)
    silent = heartbeats.sample(4, random_state=_sample_state(seed, 7))
    heartbeats.loc[silent.index, "last_event_at"] = (
        AS_OF - pd.to_timedelta(rng.uniform(36, 120, 4), unit="h")
    )
    for row in heartbeats.loc[silent.index].itertuples():
        _truth(truth, "CM-05", row.source_id, "Log source exceeded heartbeat threshold")
    return heartbeats


def make_settlement(rng: np.random.Generator, truth: list[dict],
                    seed: int = DEFAULT_SEED) -> tuple[pd.DataFrame, pd.DataFrame]:
    transaction_count = 5000
    accounts = [f"A{i:05d}" for i in range(1, 401)]
    transaction_ids = [f"T{i:07d}" for i in range(1, transaction_count + 1)]
    amounts = np.round(np.exp(rng.normal(5.6, 1.4, transaction_count)), 2)
    booked_at = AS_OF - pd.to_timedelta(
        rng.integers(0, WINDOW_DAYS, transaction_count), unit="D"
    )
    ledger = pd.DataFrame({
        "ledger_row_id": [f"LR{i:07d}" for i in range(1, transaction_count + 1)],
        "txn_id": transaction_ids,
        "account_id": rng.choice(accounts, transaction_count),
        "amount": amounts,
        "currency": "USD",
        "booked_at": booked_at,
        "reconciled": rng.random(transaction_count) > 0.02,
    })
    ledger.loc[
        (~ledger.reconciled) & (ledger.booked_at < AS_OF - pd.Timedelta(days=5)),
        "reconciled",
    ] = True
    processor = ledger[["txn_id", "amount", "booked_at"]].copy()
    processor.insert(
        0, "settlement_row_id",
        [f"SR{i:07d}" for i in range(1, len(processor) + 1)],
    )
    processor.columns = ["settlement_row_id", "txn_id", "settle_amount", "settled_at"]

    missing = processor.sample(25, random_state=_sample_state(seed, 8))
    processor = processor.drop(missing.index)
    for row in missing.itertuples():
        _truth(truth, "TR-01", row.txn_id, "Ledger item lacks processor settlement")

    mismatch = processor.sample(22, random_state=_sample_state(seed, 9))
    processor.loc[mismatch.index, "settle_amount"] = (
        processor.loc[mismatch.index, "settle_amount"]
        * rng.uniform(1.01, 1.15, len(mismatch))
    ).round(2)
    for row in processor.loc[mismatch.index].itertuples():
        _truth(truth, "TR-02", row.txn_id, "Ledger and processor amounts differ")

    duplicates = ledger.sample(
        8, random_state=_sample_state(seed, 10)
    ).copy()
    duplicates["ledger_row_id"] = [f"LRD{i:05d}" for i in range(1, len(duplicates) + 1)]
    ledger = pd.concat([ledger, duplicates], ignore_index=True)
    for row in duplicates.itertuples():
        _truth(truth, "TR-03", row.txn_id, "Transaction identifier was posted twice")

    old = ledger[
        ledger.booked_at < AS_OF - pd.Timedelta(days=20)
    ].sample(15, random_state=_sample_state(seed, 11))
    ledger.loc[old.index, "reconciled"] = False
    for row in ledger.loc[old.index].itertuples():
        _truth(truth, "TR-04", row.txn_id, "Unreconciled item exceeds the business-day threshold")

    fast_accounts = rng.choice(accounts, 4, replace=False)
    extra_ledger = []
    transaction_number = 0
    for account_id in fast_accounts:
        for _ in range(60):
            extra_ledger.append({
                "ledger_row_id": f"LRV{transaction_number:05d}",
                "txn_id": f"TV{transaction_number:05d}",
                "account_id": account_id,
                "amount": float(np.round(rng.uniform(50, 900), 2)),
                "currency": "USD",
                "booked_at": AS_OF - pd.Timedelta(days=int(rng.integers(0, 10))),
                "reconciled": True,
            })
            transaction_number += 1
        _truth(truth, "TR-05", account_id, "Account has a seeded transaction-velocity burst")

    hover_accounts = rng.choice(
        [account for account in accounts if account not in fast_accounts], 3, replace=False
    )
    for account_id in hover_accounts:
        for _ in range(6):
            extra_ledger.append({
                "ledger_row_id": f"LRH{transaction_number:05d}",
                "txn_id": f"TH{transaction_number:05d}",
                "account_id": account_id,
                "amount": float(np.round(rng.uniform(9700, 9989), 2)),
                "currency": "USD",
                "booked_at": AS_OF - pd.Timedelta(days=int(rng.integers(0, 30))),
                "reconciled": True,
            })
            transaction_number += 1
        _truth(truth, "TR-06", account_id, "Account has repeated transactions below approval limit")

    extra = pd.DataFrame(extra_ledger)
    settlement_extra = extra[["txn_id", "amount", "booked_at"]].copy()
    settlement_extra.insert(
        0, "settlement_row_id",
        [f"SRE{i:06d}" for i in range(1, len(settlement_extra) + 1)],
    )
    settlement_extra.columns = [
        "settlement_row_id", "txn_id", "settle_amount", "settled_at"
    ]
    ledger = pd.concat([ledger, extra], ignore_index=True)
    processor = pd.concat([processor, settlement_extra], ignore_index=True)
    return ledger, processor


def generate(outdir: str | Path, seed: int = DEFAULT_SEED) -> dict[str, pd.DataFrame]:
    seed = validate_seed(seed)
    rng = _rng(seed)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    truth: list[dict] = []

    users = make_users(rng)
    grants = make_grants(rng, users, truth, seed)
    auth = make_auth_logs(rng, users, grants, truth)
    changes = make_changes(rng, users, truth, seed)
    deploys = make_deploy_logs(rng, changes, truth)
    heartbeats = make_log_heartbeats(rng, truth, seed)
    ledger, processor = make_settlement(rng, truth, seed)

    frames = {
        "users": users,
        "access_grants": grants,
        "auth_logs": auth,
        "changes": changes,
        "deploy_logs": deploys,
        "log_heartbeats": heartbeats,
        "ledger": ledger,
        "processor_settlement": processor,
        "ground_truth": pd.DataFrame(truth),
    }
    for name, frame in frames.items():
        frame.to_csv(outdir / f"{name}.csv", index=False)
    return frames


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate the CCAF synthetic dataset")
    parser.add_argument("outdir", nargs="?", default="data/synthetic")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    arguments = parser.parse_args()
    generated = generate(arguments.outdir, seed=arguments.seed)
    for name, frame in generated.items():
        print(f"{name:22s} {len(frame):>7,d} rows")
