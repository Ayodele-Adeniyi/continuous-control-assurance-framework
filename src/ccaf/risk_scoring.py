"""Transparent exception prioritization and population-rate reporting."""

from __future__ import annotations

import pandas as pd

DEFAULT_REVIEW_WEIGHTS = {"Critical": 9, "High": 6, "Medium": 3, "Low": 1}


def score_exceptions(exceptions: pd.DataFrame,
                     review_weights: dict[str, float] | None = None) -> pd.DataFrame:
    """Apply configurable review weights; scores are not loss estimates."""
    weights = review_weights or DEFAULT_REVIEW_WEIGHTS
    result = exceptions.copy()
    if result.empty:
        result["review_priority_score"] = pd.Series(dtype=float)
        return result
    result["exposure_factor"] = result["exposure_factor"].clip(1.0, 2.0)
    missing = sorted(set(result.review_priority) - set(weights))
    if missing:
        raise ValueError(f"No review weight configured for: {', '.join(missing)}")
    result["review_priority_score"] = (
        result["review_priority"].map(weights).astype(float) * result["exposure_factor"]
    )
    return result


def control_summary(exceptions: pd.DataFrame,
                    evaluations: dict[str, dict[str, dict]]) -> pd.DataFrame:
    """Summarize each control test, including tests that were not evaluable."""
    rows = []
    for module, controls in evaluations.items():
        for control_id, evaluation in controls.items():
            subset = exceptions[
                (exceptions.module == module) & (exceptions.control_id == control_id)
            ]
            count = len(subset)
            population = int(evaluation["eligible_population"])
            completed = evaluation["evaluation_status"] == "Completed"
            rows.append({
                "module": module,
                "control_id": control_id,
                "control_name": evaluation["control_name"],
                "review_priority": evaluation["review_priority"],
                "evaluation_status": evaluation["evaluation_status"],
                "status_reason": evaluation["status_reason"],
                "eligible_population": population,
                "exceptions": int(count),
                "exceptions_per_1000": round(1000 * count / population, 2)
                if completed and population else None,
                "review_priority_score": round(
                    float(subset.review_priority_score.sum()), 2
                ),
            })
    return pd.DataFrame(rows).sort_values(
        ["review_priority_score", "exceptions_per_1000"],
        ascending=False,
        na_position="last",
    )


def module_summary(exceptions: pd.DataFrame,
                   evaluations: dict[str, dict[str, dict]]) -> pd.DataFrame:
    """Aggregate completed test evaluations without assigning risk tiers."""
    rows = []
    for module, controls in evaluations.items():
        subset = exceptions[exceptions.module == module]
        completed = [
            item for item in controls.values()
            if item["evaluation_status"] == "Completed"
        ]
        evaluation_count = sum(int(item["eligible_population"]) for item in completed)
        rows.append({
            "module": module,
            "tests_total": len(controls),
            "tests_completed": len(completed),
            "tests_not_evaluable": len(controls) - len(completed),
            "eligible_control_evaluations": evaluation_count,
            "exceptions": int(len(subset)),
            "exceptions_per_1000_evaluations": round(
                1000 * len(subset) / evaluation_count, 2
            ) if evaluation_count else None,
            "review_priority_score": round(
                float(subset.review_priority_score.sum()), 2
            ),
        })
    return pd.DataFrame(rows)
