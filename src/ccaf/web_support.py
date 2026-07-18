"""Reviewer-workspace helpers for isolated CCAF synthetic runs."""

from __future__ import annotations

import io
import json
import contextlib
import sys
import traceback
import zipfile
from pathlib import Path

import pandas as pd

from ccaf.generate_data import DEFAULT_SEED, validate_seed


CSV_ARTIFACTS = {
    "calibration_record": "calibration_record.csv",
    "control_summary": "control_summary.csv",
    "data_quality_findings": "data_quality_findings.csv",
    "exceptions": "exceptions_all.csv",
    "input_manifest": "input_manifest.csv",
    "module_summary": "module_summary.csv",
    "seeded_validation": "seeded_validation_summary.csv",
    "source_assurance": "source_assurance_record.csv",
}

CATALOG_COLUMNS = [
    "control_id",
    "risk",
    "control_statement",
    "automated_procedure",
    "control_test_type",
    "evidence_follow_up",
]


def execute_synthetic_run(
    root: Path,
    run_dir: Path,
    seed: int = DEFAULT_SEED,
) -> dict[str, object]:
    """Execute a reproducible synthetic demonstration in an isolated directory."""
    root = Path(root).resolve()
    run_dir = Path(run_dir).resolve()
    seed = validate_seed(seed)
    data_dir = run_dir / "synthetic_inputs"
    output_dir = run_dir / "outputs"
    run_dir.mkdir(parents=True, exist_ok=True)
    command_text = (
        f'python run_all.py --regenerate --seed {seed} --no-charts '
        f'--data-dir "{data_dir}" '
        f'--output-dir "{output_dir}"'
    )
    (run_dir / "run_command.txt").write_text(command_text + "\n", encoding="utf-8")
    console_buffer = io.StringIO()
    try:
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from run_all import run_framework

        with contextlib.redirect_stdout(console_buffer), contextlib.redirect_stderr(console_buffer):
            run_framework(
                regenerate=True,
                data_dir=data_dir,
                output_dir=output_dir,
                render_charts=False,
                synthetic_seed=seed,
            )
    except Exception as exc:
        console_buffer.write("\n" + traceback.format_exc())
        console_text = console_buffer.getvalue()
        (run_dir / "run_console.txt").write_text(console_text, encoding="utf-8")
        raise RuntimeError(f"CCAF did not complete: {exc}") from exc
    console_text = console_buffer.getvalue()
    (run_dir / "run_console.txt").write_text(console_text, encoding="utf-8")
    return {
        "run_dir": run_dir,
        "data_dir": data_dir,
        "output_dir": output_dir,
        "command": command_text,
        "console": console_text,
        "synthetic_seed": seed,
    }


def load_artifacts(output_dir: Path) -> dict[str, object]:
    """Load the reviewer-facing results from one completed run."""
    output_dir = Path(output_dir)
    artifacts: dict[str, object] = {
        name: pd.read_csv(output_dir / filename)
        for name, filename in CSV_ARTIFACTS.items()
    }
    artifacts["run_metadata"] = json.loads(
        (output_dir / "run_metadata.json").read_text(encoding="utf-8")
    )
    modules = artifacts["module_summary"]
    controls = artifacts["control_summary"]
    exceptions = artifacts["exceptions"]
    validation = artifacts["seeded_validation"]
    assert isinstance(modules, pd.DataFrame)
    assert isinstance(controls, pd.DataFrame)
    assert isinstance(exceptions, pd.DataFrame)
    assert isinstance(validation, pd.DataFrame)
    artifacts["metrics"] = {
        "tests": int(len(controls)),
        "evaluations": int(modules["eligible_control_evaluations"].sum()),
        "exceptions": int(len(exceptions)),
        "seeded_conditions": int(validation["seeded_conditions"].sum()),
        "seeded_detected": int(validation["seeded_conditions_detected"].sum()),
    }
    return artifacts


def load_control_catalog(path: Path) -> pd.DataFrame:
    """Read the six-column practitioner catalog into reviewer-facing records."""
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.startswith(("| PA-", "| CM-", "| TR-")):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != len(CATALOG_COLUMNS):
            raise ValueError(f"Unexpected control-catalog row: {line}")
        rows.append(cells)
    catalog = pd.DataFrame(rows, columns=CATALOG_COLUMNS)
    if len(catalog) != 20 or catalog["control_id"].nunique() != 20:
        raise ValueError("The reviewer catalog must contain exactly 20 unique control tests")
    return catalog


def build_evidence_zip(
    data_dir: Path,
    output_dir: Path,
    run_dir: Path | None = None,
) -> bytes:
    """Package inputs, outputs, and run records for reviewer download."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for label, directory in (
            ("synthetic_inputs", Path(data_dir)),
            ("outputs", Path(output_dir)),
        ):
            for path in sorted(directory.rglob("*")):
                if path.is_file():
                    archive.write(path, Path(label) / path.relative_to(directory))
        if run_dir:
            for name in ("run_command.txt", "run_console.txt"):
                path = Path(run_dir) / name
                if path.exists():
                    archive.write(path, Path("run_record") / name)
    return buffer.getvalue()


def render_review_response(values: dict[str, object]) -> str:
    """Render reviewer-authored responses without drafting their opinions."""
    procedures = values.get("procedures", [])
    procedure_lines = "\n".join(f"- [x] {item}" for item in procedures)
    if not procedure_lines:
        procedure_lines = "- [ ] No procedure selected"
    return f"""# Independent Technical Review Response

## Reviewer and scope

**Reviewer name and role:** {values.get('reviewer', '')}

**Relevant experience:** {values.get('experience', '')}

**Review date:** {values.get('review_date', '')}

**Prior relationship, conflict, or compensation, if any:** {values.get('relationship', '')}

**Review depth:** {values.get('depth', '')}

## Release facts and procedures

- **Framework:** Continuous Control Assurance Framework (CCAF)
- **Release reviewed:** Version 1.3.1 (`v1.3.1`)
- **Review workspace:** https://continuous-control-assurance.streamlit.app/
- **Repository:** https://github.com/Ayodele-Adeniyi/continuous-control-assurance-framework
- **License:** Apache-2.0
- **Documented scope:** 20 control tests using synthetic demonstration data
- **Documented release claim:** 165 of 165 deliberately planted conditions detected
- **Synthetic seed personally observed:** {values.get('synthetic_seed', '')}
- **Run classification:** {values.get('benchmark_status', '')}

**Procedures personally performed:**

{procedure_lines}

**Result observed by reviewer, if reproduced:** {values.get('observed_result', '')}

## Reviewer-authored professional opinion

### Technical soundness

{values.get('soundness', '')}

### Claims and limitations

{values.get('boundaries', '')}

### Transferability

{values.get('transferability', '')}

### Observations

{values.get('observations', '')}

## Confirmation

This response may be cited publicly and in professional or immigration-related submissions as evidence of independent review.

This response reflects my independent professional judgment concerning the release and procedures identified above. It does not claim institutional adoption, regulatory approval, certification, or production performance.

**Name:** {values.get('reviewer', '')}

**Signature:** ______________________________

**Date:** {values.get('review_date', '')}
"""
