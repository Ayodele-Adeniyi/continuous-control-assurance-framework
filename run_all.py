"""CCAF end-to-end runner.

Generates or loads synthetic data, validates the input extracts, executes all 20
control tests, writes audit-trail artifacts, and optionally renders dashboards.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ccaf import generate_data
from ccaf import risk_scoring as scoring
from ccaf.audit_artifacts import (
    write_calibration_record,
    write_input_manifest,
    write_run_metadata,
    write_source_assurance_record,
)
from ccaf.config import load_config
from ccaf.data_quality import (
    has_blocking_findings,
    normalize_boolean_fields,
    validate_frames,
)
from ccaf.modules import change_logging, privileged_access, reconciliation
from ccaf.validation import ground_truth_summary

DATA = ROOT / "data" / "synthetic"
OUT = ROOT / "output"
DEFAULT_CONFIG = ROOT / "config" / "defaults.json"

REQUIRED_DATE_COLUMNS = {
    "users": ["hire_date", "termination_date"],
    "access_grants": ["granted_at", "expires_at"],
    "auth_logs": ["timestamp"],
    "changes": ["approved_at", "implemented_at"],
    "deploy_logs": ["deployed_at"],
    "log_heartbeats": ["last_event_at"],
    "ledger": ["booked_at"],
    "processor_settlement": ["settled_at"],
}
OPTIONAL_DATE_COLUMNS = {"ground_truth": []}

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low"]
SEVERITY_COLORS = {
    "Critical": "#b3261e", "High": "#e8710a",
    "Medium": "#f2c94c", "Low": "#7fb069",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CCAF demonstration")
    parser.add_argument("--regenerate", action="store_true", help="regenerate seeded data")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                        help="path to JSON configuration")
    parser.add_argument("--data-dir", type=Path, default=DATA,
                        help="directory containing authorized CCAF CSV extracts")
    parser.add_argument("--output-dir", type=Path, default=OUT,
                        help="directory for generated exception and run artifacts")
    parser.add_argument("--no-charts", action="store_true",
                        help="skip dashboard rendering")
    return parser.parse_args()


def load_or_generate(regenerate: bool, data_dir: Path = DATA) -> dict[str, pd.DataFrame]:
    """Load authorized extracts; synthetic ground-truth labels are optional."""
    data_dir = Path(data_dir)
    expected = [data_dir / f"{name}.csv" for name in REQUIRED_DATE_COLUMNS]
    if regenerate:
        print("Generating seeded synthetic dataset ...")
        return generate_data.generate(data_dir)
    if not all(path.exists() for path in expected):
        if data_dir.resolve() == DATA.resolve():
            print("Generating seeded synthetic dataset ...")
            return generate_data.generate(data_dir)
        missing = [path.name for path in expected if not path.exists()]
        raise FileNotFoundError(
            "Required extracts are missing from "
            f"{data_dir}: {', '.join(missing)}"
        )

    frames: dict[str, pd.DataFrame] = {}
    columns_by_dataset = dict(REQUIRED_DATE_COLUMNS)
    for name, date_columns in OPTIONAL_DATE_COLUMNS.items():
        if (data_dir / f"{name}.csv").exists():
            columns_by_dataset[name] = date_columns
    for name, date_columns in columns_by_dataset.items():
        frame = pd.read_csv(data_dir / f"{name}.csv")
        for column in date_columns:
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
        frames[name] = frame
    return frames


def run_modules(frames: dict[str, pd.DataFrame], as_of: pd.Timestamp,
                config: dict) -> tuple[pd.DataFrame, dict[str, dict[str, int]]]:
    exceptions_1, populations_1 = privileged_access.run(
        frames["users"], frames["access_grants"], frames["auth_logs"], as_of,
        config["privileged_access"],
    )
    exceptions_2, populations_2 = change_logging.run(
        frames["changes"], frames["deploy_logs"], frames["log_heartbeats"], as_of,
        config["change_logging"],
    )
    exceptions_3, populations_3 = reconciliation.run(
        frames["ledger"], frames["processor_settlement"], as_of,
        config["reconciliation"],
    )
    exceptions = pd.concat(
        [exceptions_1, exceptions_2, exceptions_3], ignore_index=True
    )
    exceptions.insert(
        0, "exception_id", [f"EX{number:05d}" for number in range(1, len(exceptions) + 1)]
    )
    exceptions["detected_at"] = as_of
    populations = {
        privileged_access.MODULE: populations_1,
        change_logging.MODULE: populations_2,
        reconciliation.MODULE: populations_3,
    }
    return exceptions, populations


def render_dashboards(exceptions: pd.DataFrame, modules: pd.DataFrame,
                      ledger: pd.DataFrame, as_of: pd.Timestamp,
                      dash_dir: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "Dashboard rendering requires matplotlib; run pip install -r requirements.txt"
        ) from exc

    dash_dir.mkdir(parents=True, exist_ok=True)
    for stale in dash_dir.glob("*.png"):
        stale.unlink()
    plt.rcParams.update({
        "figure.dpi": 150,
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

    grouped = (
        exceptions.groupby(["control_id", "severity"]).size().unstack(fill_value=0)
        .reindex(columns=[
            severity for severity in SEVERITY_ORDER
            if severity in exceptions.severity.unique()
        ], fill_value=0)
    )
    grouped = grouped.loc[grouped.sum(axis=1).sort_values().index]
    figure, axis = plt.subplots(figsize=(8, 5.5))
    left = pd.Series(0, index=grouped.index, dtype=float)
    for severity in grouped.columns:
        axis.barh(
            grouped.index, grouped[severity], left=left,
            color=SEVERITY_COLORS[severity], label=severity,
        )
        left += grouped[severity]
    axis.set_title("CCAF - Exceptions by control test (synthetic demonstration)")
    axis.set_xlabel("Reported exceptions")
    axis.legend(title="Severity", loc="lower right")
    figure.tight_layout()
    figure.savefig(dash_dir / "01_exceptions_by_control.png")
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(7.5, 4.2))
    axis.bar(
        modules.module,
        modules.exceptions_per_1000_evaluations,
        color=["#376a91", "#5f8d4e", "#b36b32"], width=0.55,
    )
    for position, value in enumerate(modules.exceptions_per_1000_evaluations):
        axis.text(position, value + 0.7, f"{value:.1f}", ha="center", fontsize=9)
    axis.set_title("CCAF - Exceptions per 1,000 eligible control evaluations")
    axis.set_ylabel("Exceptions per 1,000 evaluations")
    axis.tick_params(axis="x", rotation=8)
    figure.tight_layout()
    figure.savefig(dash_dir / "02_module_exception_rate.png")
    plt.close(figure)

    grouped = (
        exceptions.groupby(["module", "severity"]).size().unstack(fill_value=0)
        .reindex(columns=[
            severity for severity in SEVERITY_ORDER
            if severity in exceptions.severity.unique()
        ], fill_value=0)
    )
    figure, axis = plt.subplots(figsize=(7.5, 4.2))
    bottom = pd.Series(0, index=grouped.index, dtype=float)
    for severity in grouped.columns:
        axis.bar(
            grouped.index, grouped[severity], bottom=bottom,
            color=SEVERITY_COLORS[severity], label=severity, width=0.5,
        )
        bottom += grouped[severity]
    axis.set_title("CCAF - Exception severity mix by module")
    axis.set_ylabel("Reported exceptions")
    axis.legend(title="Severity")
    axis.tick_params(axis="x", rotation=8)
    figure.tight_layout()
    figure.savefig(dash_dir / "03_severity_by_module.png")
    plt.close(figure)

    unreconciled = ledger[~ledger.reconciled.astype(bool)].copy()
    unreconciled["business_days"] = reconciliation.business_days_elapsed(
        unreconciled.booked_at, as_of
    )
    bins = [-1, 5, 15, 30, 60, 10000]
    labels = ["0-5", "6-15", "16-30", "31-60", "60+"]
    aging = pd.cut(
        unreconciled.business_days, bins=bins, labels=labels
    ).value_counts().reindex(labels, fill_value=0)
    figure, axis = plt.subplots(figsize=(7, 4))
    axis.bar(
        aging.index, aging.values,
        color=["#7fb069", "#f2c94c", "#e8710a", "#b3261e", "#7a1710"],
        width=0.55,
    )
    axis.axvline(0.5, ls="--", lw=0.8, color="#666")
    axis.text(
        0.55, axis.get_ylim()[1] * 0.95,
        "TR-04 demonstration threshold: 5 weekdays",
        fontsize=7.5, color="#666", va="top",
    )
    axis.set_title("CCAF - Weekday aging of unreconciled ledger items")
    axis.set_ylabel("Open items")
    axis.set_xlabel("Weekdays elapsed (holidays require local calendar)")
    figure.tight_layout()
    figure.savefig(dash_dir / "04_reconciliation_aging.png")
    plt.close(figure)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    as_of = pd.Timestamp(config["as_of"])
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    data_dir = args.data_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    frames = load_or_generate(args.regenerate, data_dir)
    findings = validate_frames(frames)
    findings.to_csv(output_dir / "data_quality_findings.csv", index=False)
    write_input_manifest(data_dir, frames, output_dir / "input_manifest.csv")
    write_source_assurance_record(frames, output_dir / "source_assurance_record.csv")
    write_calibration_record(config, output_dir / "calibration_record.csv")
    write_run_metadata(config, version, output_dir / "run_metadata.json")
    if has_blocking_findings(findings):
        raise ValueError(
            "Blocking data-quality findings were written to "
            f"{output_dir / 'data_quality_findings.csv'}"
        )
    frames = normalize_boolean_fields(frames)

    exceptions, populations = run_modules(frames, as_of, config)
    exceptions = scoring.score_exceptions(
        exceptions, config["scoring"]["impact_weights"]
    )
    controls = scoring.control_summary(exceptions, populations)
    modules = scoring.module_summary(exceptions, populations)
    validation = (
        ground_truth_summary(exceptions, frames["ground_truth"])
        if "ground_truth" in frames
        else ground_truth_summary(exceptions, None)
    )

    exceptions.to_csv(output_dir / "exceptions_all.csv", index=False)
    for module, subset in exceptions.groupby("module"):
        slug = module.split(" ")[0].lower()
        subset.to_csv(output_dir / f"exceptions_{slug}.csv", index=False)
    controls.to_csv(output_dir / "control_summary.csv", index=False)
    modules.to_csv(output_dir / "risk_summary.csv", index=False)
    validation.to_csv(output_dir / "seeded_validation_summary.csv", index=False)

    if not args.no_charts:
        render_dashboards(
            exceptions, modules, frames["ledger"], as_of,
            output_dir / "dashboards",
        )

    evaluations = int(modules.control_evaluations.sum())
    print(
        f"\nCCAF {version} run @ {as_of:%Y-%m-%d} | "
        f"eligible control evaluations: {evaluations:,d} | "
        f"exceptions: {len(exceptions):,d}\n"
    )
    print(modules.to_string(index=False))
    if "ground_truth" in frames:
        print("\nSeeded-condition validation:")
        print(validation.to_string(index=False))
    else:
        print("\nSeeded-condition validation: not supplied for this run")
    print(f"\nOutputs -> {output_dir}")


if __name__ == "__main__":
    main()
