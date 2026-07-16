"""Transparent exception prioritization and population-rate reporting."""

from __future__ import annotations

import pandas as pd

DEFAULT_IMPACT = {"Critical": 9, "High": 6, "Medium": 3, "Low": 1}


def score_exceptions(exceptions: pd.DataFrame,
                     impact_weights: dict[str, float] | None = None) -> pd.DataFrame:
    """Apply configurable review-priority weights; scores are not loss estimates."""
    weights = impact_weights or DEFAULT_IMPACT
    result = exceptions.copy()
    result["exposure_factor"] = result["exposure_factor"].clip(1.0, 2.0)
    missing = sorted(set(result.severity) - set(weights))
    if missing:
        raise ValueError(f"No impact weight configured for: {', '.join(missing)}")
    result["priority_score"] = (
        result["severity"].map(weights).astype(float) * result["exposure_factor"]
    )
    return result


def control_summary(exceptions: pd.DataFrame,
                    populations: dict[str, dict[str, int]]) -> pd.DataFrame:
    """Summarize each control against its own eligible population."""
    rows = []
    for module, controls in populations.items():
        for control_id, population in controls.items():
            subset = exceptions[
                (exceptions.module == module) & (exceptions.control_id == control_id)
            ]
            count = len(subset)
            rows.append({
                "module": module,
                "control_id": control_id,
                "control_name": subset.control_name.iloc[0] if count else "",
                "severity": subset.severity.iloc[0] if count else "",
                "eligible_population": int(population),
                "exceptions": int(count),
                "exceptions_per_1000": round(1000 * count / population, 2)
                if population else None,
                "priority_score": round(float(subset.priority_score.sum()), 2),
            })
    return pd.DataFrame(rows).sort_values(
        ["priority_score", "exceptions_per_1000"], ascending=False
    )


def module_summary(exceptions: pd.DataFrame,
                   populations: dict[str, dict[str, int]]) -> pd.DataFrame:
    """Aggregate transparent control-evaluation counts without assigning risk tiers."""
    rows = []
    for module, controls in populations.items():
        subset = exceptions[exceptions.module == module]
        evaluations = sum(int(value) for value in controls.values())
        rows.append({
            "module": module,
            "controls_executed": len(controls),
            "control_evaluations": evaluations,
            "exceptions": int(len(subset)),
            "exceptions_per_1000_evaluations": round(
                1000 * len(subset) / evaluations, 2
            ) if evaluations else None,
            "priority_score": round(float(subset.priority_score.sum()), 2),
        })
    return pd.DataFrame(rows)
