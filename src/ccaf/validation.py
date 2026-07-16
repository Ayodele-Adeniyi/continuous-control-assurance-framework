"""Validation of synthetic seeded conditions against reported exceptions."""

from __future__ import annotations

import pandas as pd

VALIDATION_COLUMNS = [
    "control_id",
    "seeded_conditions",
    "seeded_conditions_detected",
    "seeded_recall",
    "reported_unique_entities",
    "additional_synthetic_exceptions",
]

def ground_truth_summary(exceptions: pd.DataFrame,
                         truth: pd.DataFrame | None) -> pd.DataFrame:
    """Report recall of deliberately seeded synthetic conditions by control."""
    if truth is None:
        return pd.DataFrame(columns=VALIDATION_COLUMNS)
    reported = exceptions[["control_id", "entity_id"]].drop_duplicates().copy()
    seeded = truth[["control_id", "entity_id"]].drop_duplicates().copy()
    matched = seeded.merge(reported, on=["control_id", "entity_id"], how="left", indicator=True)
    matched["detected"] = matched["_merge"].eq("both")

    rows = []
    controls = sorted(set(seeded.control_id) | set(reported.control_id))
    for control_id in controls:
        seeded_control = matched[matched.control_id == control_id]
        reported_control = reported[reported.control_id == control_id]
        seeded_count = len(seeded_control)
        detected_count = int(seeded_control.detected.sum()) if seeded_count else 0
        reported_count = len(reported_control)
        reported_matches = reported_control.merge(
            seeded[seeded.control_id == control_id],
            on=["control_id", "entity_id"], how="inner",
        )
        rows.append({
            "control_id": control_id,
            "seeded_conditions": seeded_count,
            "seeded_conditions_detected": detected_count,
            "seeded_recall": round(detected_count / seeded_count, 4) if seeded_count else None,
            "reported_unique_entities": reported_count,
            "additional_synthetic_exceptions": reported_count - len(reported_matches),
        })
    return pd.DataFrame(rows, columns=VALIDATION_COLUMNS)
