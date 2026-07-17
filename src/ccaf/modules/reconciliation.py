"""Module 3 - Transaction Reconciliation and Payment Anomaly."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ccaf.results import COMPLETED, NOT_EVALUABLE, evaluation, exception_frame

MODULE = "M3 Reconciliation & Payments"
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


def _value_exposure(amount: float) -> float:
    if amount >= 10_000:
        return 2.0
    if amount >= 1_000:
        return 1.5
    if amount >= 100:
        return 1.2
    return 1.0


def business_days_elapsed(start: pd.Series, as_of: pd.Timestamp) -> pd.Series:
    """Count weekdays in [start date, as-of date); holidays require local calibration."""
    starts = pd.to_datetime(start).values.astype("datetime64[D]")
    end = np.datetime64(as_of.normalize(), "D")
    return pd.Series(np.busday_count(starts, end), index=start.index)


def run(ledger: pd.DataFrame, processor: pd.DataFrame, as_of: pd.Timestamp,
        config: dict) -> tuple[pd.DataFrame, dict[str, dict]]:
    out: list[dict] = []
    merged = ledger.merge(processor, on="txn_id", how="left", suffixes=("", "_p"))

    settlement_grace_days = int(config["settlement_grace_days"])
    settlement_due = merged[
        merged.booked_at.le(as_of - pd.Timedelta(days=settlement_grace_days))
    ]
    hits = settlement_due[settlement_due.settle_amount.isna()]
    for row in hits.itertuples():
        out.append(_ex(
            "TR-01", "Ledger item with no processor settlement record", "High",
            row.txn_id, f"acct {row.account_id}; amount {row.amount:,.2f} unmatched",
            exposure=_value_exposure(row.amount),
        ))

    matched = merged[merged.settle_amount.notna()].copy()
    difference = (matched.amount - matched.settle_amount).abs()
    tolerance = float(config["amount_tolerance"])
    hits = matched[difference > tolerance + 1e-9]
    for row in hits.itertuples():
        amount_difference = abs(row.amount - row.settle_amount)
        out.append(_ex(
            "TR-02", "Ledger/processor amount mismatch", "High", row.txn_id,
            f"ledger {row.amount:,.2f} vs processor {row.settle_amount:,.2f}; "
            f"difference {amount_difference:,.2f}",
            exposure=_value_exposure(amount_difference),
        ))

    duplicates = ledger[ledger.duplicated("txn_id", keep=False)]
    for transaction_id, group in duplicates.groupby("txn_id"):
        amount = float(group.amount.iloc[0])
        out.append(_ex(
            "TR-03", "Duplicate transaction identifier", "Critical", transaction_id,
            f"{len(group)} ledger postings of {amount:,.2f}",
            exposure=_value_exposure(amount),
        ))

    unreconciled = ledger[~ledger.reconciled.astype(bool)].copy()
    unreconciled["age_business_days"] = business_days_elapsed(
        unreconciled.booked_at, as_of
    )
    aging_threshold = int(config["aging_business_days"])
    hits = unreconciled[unreconciled.age_business_days > aging_threshold]
    for row in hits.itertuples():
        out.append(_ex(
            "TR-04", "Unreconciled item aged beyond threshold", "Medium", row.txn_id,
            f"acct {row.account_id}; open {row.age_business_days} business days; "
            f"amount {row.amount:,.2f}",
            exposure=min(2.0, 1.0 + row.age_business_days / 45),
        ))

    recent_days = int(config["recent_window_days"])
    recent = ledger[ledger.booked_at >= as_of - pd.Timedelta(days=recent_days)]
    counts = recent.groupby("account_id")["txn_id"].count()
    minimum_comparison = int(config["minimum_comparison_population"])
    tr05_status = COMPLETED
    tr05_reason = ""
    if len(counts) < minimum_comparison:
        tr05_status = NOT_EVALUABLE
        tr05_reason = (
            f"requires at least {minimum_comparison} active accounts in the comparison "
            f"population; {len(counts)} supplied"
        )
    else:
        median = counts.median()
        mad = (counts - median).abs().median()
        if mad > 0:
            robust_z = 0.6745 * (counts - median) / mad
            threshold = float(config["robust_z_threshold"])
            for account_id, z_value in robust_z[robust_z >= threshold].items():
                out.append(_ex(
                    "TR-05", "Account transaction-velocity outlier", "Medium",
                    account_id,
                    f"{int(counts[account_id])} transactions in {recent_days}d "
                    f"(robust z={z_value:.1f})",
                    exposure=min(2.0, 1.0 + float(z_value) / 10),
                ))
        else:
            tr05_status = NOT_EVALUABLE
            tr05_reason = "comparison population has no usable variation in transaction counts"

    limit = float(config["approval_limit"])
    low = float(config["hover_low"])
    high = float(config["hover_high"])
    band = ledger[(ledger.amount >= low * limit) & (ledger.amount < high * limit)]
    counts = band.groupby("account_id")["txn_id"].count()
    minimum = int(config["hover_min_count"])
    for account_id, count in counts[counts >= minimum].items():
        out.append(_ex(
            "TR-06", "Threshold hovering below approval limit", "High", account_id,
            f"{int(count)} transactions within {low:.0%}-{high:.1%} of "
            f"{limit:,.0f} demonstration limit", exposure=1.5,
        ))

    evaluations = {
        "TR-01": evaluation(
            "Ledger item with no processor settlement record", "High", len(settlement_due)
        ),
        "TR-02": evaluation("Ledger/processor amount mismatch", "High", len(matched)),
        "TR-03": evaluation("Duplicate transaction identifier", "Critical", ledger.txn_id.nunique()),
        "TR-04": evaluation(
            "Unreconciled item aged beyond threshold", "Medium", len(unreconciled)
        ),
        "TR-05": evaluation(
            "Account transaction-velocity outlier", "Medium", recent.account_id.nunique(),
            tr05_status, tr05_reason,
        ),
        "TR-06": evaluation(
            "Threshold hovering below approval limit", "High", ledger.account_id.nunique()
        ),
    }
    return exception_frame(out), evaluations
