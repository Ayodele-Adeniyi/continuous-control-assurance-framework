"""Shared result contracts for CCAF control-test execution."""

from __future__ import annotations

from typing import Any

import pandas as pd


EXCEPTION_COLUMNS = [
    "module",
    "control_id",
    "control_name",
    "review_priority",
    "entity_id",
    "detail",
    "exposure_factor",
    "rule_version",
]

COMPLETED = "Completed"
NOT_EVALUABLE = "Not Evaluable"


def exception_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Return exception rows with a stable schema, including for clean runs."""
    return pd.DataFrame(rows, columns=EXCEPTION_COLUMNS)


def evaluation(
    control_name: str,
    review_priority: str,
    eligible_population: int,
    status: str = COMPLETED,
    status_reason: str = "",
) -> dict[str, Any]:
    """Create one explicit control-test evaluation record."""
    if status not in {COMPLETED, NOT_EVALUABLE}:
        raise ValueError(f"Unsupported evaluation status: {status}")
    return {
        "control_name": control_name,
        "review_priority": review_priority,
        "eligible_population": int(eligible_population),
        "evaluation_status": status,
        "status_reason": status_reason,
    }
