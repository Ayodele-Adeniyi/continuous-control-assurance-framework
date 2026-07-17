"""Regression and validation tests for the CCAF synthetic demonstration."""

from __future__ import annotations

import hashlib
import shutil
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TEST_TEMP = ROOT / ".test_tmp"
TEST_TEMP.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from ccaf import __version__, generate_data
from ccaf.config import load_config
from ccaf.data_quality import (
    has_blocking_findings,
    normalize_boolean_fields,
    validate_frames,
)
from ccaf import risk_scoring
from ccaf.audit_artifacts import write_source_assurance_record
from ccaf.modules import change_logging, privileged_access, reconciliation
from ccaf.results import COMPLETED, NOT_EVALUABLE, exception_frame
from ccaf.validation import ground_truth_summary
from run_all import load_or_generate, run_modules


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _case_directory(name: str) -> Path:
    path = TEST_TEMP / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


class FrameworkTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(TEST_TEMP, ignore_errors=True)

    def test_package_version_matches_release(self) -> None:
        self.assertEqual(__version__, "1.3.1")

    def setUp(self) -> None:
        self.config = load_config(ROOT / "config" / "defaults.json")

    def test_seeded_generation_is_reproducible(self) -> None:
        first = _case_directory("reproducibility_first")
        second = _case_directory("reproducibility_second")
        generate_data.generate(first)
        generate_data.generate(second)
        first_paths = sorted(first.glob("*.csv"))
        second_paths = sorted(second.glob("*.csv"))
        self.assertEqual([path.name for path in first_paths], [path.name for path in second_paths])
        self.assertEqual([_hash(path) for path in first_paths], [_hash(path) for path in second_paths])

    def test_all_seeded_conditions_are_detected(self) -> None:
        directory = _case_directory("seeded_detection")
        frames = generate_data.generate(directory)
        exceptions, evaluations = run_modules(
            frames, pd.Timestamp(self.config["as_of"]), self.config
        )
        summary = ground_truth_summary(exceptions, frames["ground_truth"])
        self.assertEqual(set(summary.control_id), {
            "PA-01", "PA-02", "PA-03", "PA-04", "PA-05", "PA-06", "PA-07",
            "CM-01", "CM-02", "CM-03", "CM-04", "CM-05", "CM-06", "CM-07",
            "TR-01", "TR-02", "TR-03", "TR-04", "TR-05", "TR-06",
        })
        self.assertTrue((summary.seeded_recall == 1.0).all(), summary.to_string())
        self.assertTrue(all(
            item["evaluation_status"] == COMPLETED
            for module in evaluations.values() for item in module.values()
        ))

    def test_generated_data_passes_preconditions(self) -> None:
        directory = _case_directory("data_quality_clean")
        frames = generate_data.generate(directory)
        findings = validate_frames(frames)
        self.assertFalse(has_blocking_findings(findings), findings.to_string())

    def test_ground_truth_is_optional_for_authorized_extracts(self) -> None:
        directory = _case_directory("without_ground_truth")
        generate_data.generate(directory)
        (directory / "ground_truth.csv").unlink()
        frames = load_or_generate(False, directory)
        self.assertNotIn("ground_truth", frames)
        findings = validate_frames(frames)
        self.assertFalse(has_blocking_findings(findings), findings.to_string())
        exceptions, evaluations = run_modules(
            frames, pd.Timestamp(self.config["as_of"]), self.config
        )
        self.assertEqual(len(evaluations), 3)
        self.assertEqual(exceptions.control_id.nunique(), 20)

    def test_data_quality_detects_duplicate_key_and_orphan(self) -> None:
        directory = _case_directory("data_quality_bad")
        frames = generate_data.generate(directory)
        duplicate = frames["users"].iloc[[0]].copy()
        frames["users"] = pd.concat([frames["users"], duplicate], ignore_index=True)
        frames["access_grants"].loc[0, "user_id"] = "UNKNOWN-USER"
        findings = validate_frames(frames)
        self.assertIn("DQ-004", set(findings.check_id))
        self.assertIn("DQ-006", set(findings.check_id))
        self.assertTrue(has_blocking_findings(findings))

    def test_data_quality_requires_expiry_for_temporary_access(self) -> None:
        directory = _case_directory("data_quality_temporary_access")
        frames = generate_data.generate(directory)
        index = frames["access_grants"].index[0]
        frames["access_grants"].loc[index, ["temporary", "grant_status", "expires_at"]] = [
            True, "active", pd.NaT,
        ]
        findings = validate_frames(frames)
        self.assertIn("DQ-011", set(findings.check_id))
        self.assertTrue(has_blocking_findings(findings))

    def test_boolean_strings_are_normalized_after_validation(self) -> None:
        directory = _case_directory("boolean_strings")
        frames = generate_data.generate(directory)
        frames["access_grants"]["privileged"] = frames["access_grants"][
            "privileged"
        ].map({True: "1", False: "0"})
        findings = validate_frames(frames)
        self.assertFalse(has_blocking_findings(findings), findings.to_string())
        normalized = normalize_boolean_fields(frames)
        self.assertTrue(pd.api.types.is_bool_dtype(
            normalized["access_grants"]["privileged"]
        ))

    def test_missing_boolean_is_blocking(self) -> None:
        directory = _case_directory("missing_boolean")
        frames = generate_data.generate(directory)
        frames["changes"]["emergency"] = frames["changes"]["emergency"].astype(object)
        frames["changes"].loc[0, "emergency"] = None
        findings = validate_frames(frames)
        self.assertIn("DQ-010", set(findings.check_id))
        self.assertTrue(has_blocking_findings(findings))

    def test_missing_change_category_is_blocking(self) -> None:
        directory = _case_directory("missing_change_category")
        frames = generate_data.generate(directory)
        frames["changes"] = frames["changes"].drop(columns=["category"])
        findings = validate_frames(frames)
        self.assertIn("DQ-002", set(findings.check_id))
        self.assertTrue(has_blocking_findings(findings))

    def test_reconciliation_aging_uses_weekdays(self) -> None:
        start = pd.Series(pd.to_datetime(["2026-06-26", "2026-06-29"]))  # Friday, Monday
        as_of = pd.Timestamp("2026-07-06")  # following Monday
        elapsed = reconciliation.business_days_elapsed(start, as_of)
        self.assertEqual(elapsed.tolist(), [6, 5])

    def test_failed_authentication_does_not_reset_dormancy(self) -> None:
        users = pd.DataFrame([{
            "user_id": "U1", "status": "active",
            "hire_date": pd.Timestamp("2020-01-01"),
            "termination_date": pd.NaT,
        }])
        grants = pd.DataFrame([{
            "grant_id": "G1", "user_id": "U1", "entitlement": "DB_ADMIN",
            "privileged": True, "granted_at": pd.Timestamp("2025-01-01"),
            "approved_by": "U2", "grant_status": "active",
            "temporary": False, "expires_at": pd.NaT,
        }])
        auth = pd.DataFrame([{
            "event_id": "E1", "user_id": "U1", "system": "core-banking",
            "timestamp": pd.Timestamp("2026-04-20"), "success": False,
        }])
        exceptions, evaluations = privileged_access.run(
            users, grants, auth, pd.Timestamp("2026-07-01"),
            self.config["privileged_access"],
        )
        dormant = exceptions[exceptions.control_id.eq("PA-04")]
        self.assertEqual(dormant.entity_id.tolist(), ["U1"])
        self.assertFalse(exceptions.control_id.eq("PA-06").any())
        self.assertEqual(evaluations["PA-04"]["evaluation_status"], COMPLETED)
        self.assertEqual(evaluations["PA-06"]["evaluation_status"], NOT_EVALUABLE)

    def test_change_boundaries_and_evaluation_status(self) -> None:
        changes = pd.DataFrame([{
            "change_id": "C1", "system": "core", "category": "normal",
            "approved_by": "U2", "implemented_by": "U3", "approved_at": pd.NaT,
            "implemented_at": pd.Timestamp("2026-06-30"), "emergency": False,
            "pir_completed": False, "test_completed": True, "test_approved_by": "U2",
        }])
        deploys = pd.DataFrame([{
            "deploy_id": "D1", "system": "core",
            "deployed_at": pd.Timestamp("2026-06-30"), "change_id": "C1",
        }])
        heartbeats = pd.DataFrame([{
            "source_id": "S1", "system": "core", "log_source": "app",
            "last_event_at": pd.Timestamp("2026-06-30"),
        }])
        exceptions, evaluations = change_logging.run(
            changes, deploys, heartbeats, pd.Timestamp("2026-07-01"),
            self.config["change_logging"],
        )
        self.assertEqual(
            set(exceptions.control_id), {"CM-01", "CM-05"}
        )
        self.assertEqual(evaluations["CM-06"]["evaluation_status"], NOT_EVALUABLE)

    def test_reconciliation_uses_unreconciled_population_and_boundaries(self) -> None:
        ledger = pd.DataFrame([
            {
                "ledger_row_id": "L1", "txn_id": "T1", "account_id": "A1",
                "amount": 100.00, "booked_at": pd.Timestamp("2026-06-29"),
                "reconciled": True,
            },
            {
                "ledger_row_id": "L2", "txn_id": "T2", "account_id": "A2",
                "amount": 200.00, "booked_at": pd.Timestamp("2026-06-22"),
                "reconciled": False,
            },
        ])
        processor = pd.DataFrame([
            {
                "settlement_row_id": "S1", "txn_id": "T1", "settle_amount": 99.99,
                "settled_at": pd.Timestamp("2026-06-29"),
            },
            {
                "settlement_row_id": "S2", "txn_id": "T2", "settle_amount": 200.00,
                "settled_at": pd.Timestamp("2026-06-22"),
            },
        ])
        exceptions, evaluations = reconciliation.run(
            ledger, processor, pd.Timestamp("2026-07-01"), self.config["reconciliation"]
        )
        self.assertFalse(exceptions.control_id.eq("TR-02").any())
        self.assertTrue(exceptions.control_id.eq("TR-04").any())
        self.assertEqual(evaluations["TR-04"]["eligible_population"], 1)
        self.assertEqual(evaluations["TR-05"]["evaluation_status"], NOT_EVALUABLE)

    def test_temporary_access_expiry_boundary(self) -> None:
        users = pd.DataFrame([
            {"user_id": "U1", "status": "active", "hire_date": pd.Timestamp("2020-01-01"), "termination_date": pd.NaT},
            {"user_id": "U2", "status": "active", "hire_date": pd.Timestamp("2020-01-01"), "termination_date": pd.NaT},
        ])
        grants = pd.DataFrame([
            {
                "grant_id": "G1", "user_id": "U1", "entitlement": "DB_ADMIN",
                "privileged": True, "granted_at": pd.Timestamp("2026-06-01"),
                "approved_by": "U2", "grant_status": "active", "temporary": True,
                "expires_at": pd.Timestamp("2026-07-01"),
            },
            {
                "grant_id": "G2", "user_id": "U2", "entitlement": "DB_ADMIN",
                "privileged": True, "granted_at": pd.Timestamp("2026-06-01"),
                "approved_by": "U1", "grant_status": "active", "temporary": True,
                "expires_at": pd.Timestamp("2026-06-30 23:59:59"),
            },
        ])
        auth = pd.DataFrame([{
            "event_id": "E1", "user_id": "U1", "system": "core",
            "timestamp": pd.Timestamp("2026-04-01"), "success": True,
        }])
        exceptions, _ = privileged_access.run(
            users, grants, auth, pd.Timestamp("2026-07-01"),
            self.config["privileged_access"],
        )
        expired = exceptions[exceptions.control_id.eq("PA-07")]
        self.assertEqual(expired.entity_id.tolist(), ["G2"])

    def test_clean_exception_set_is_reported_without_failure(self) -> None:
        clean = risk_scoring.score_exceptions(exception_frame([]))
        evaluations = {
            "Example module": {
                "EX-01": {
                    "control_name": "Example test",
                    "review_priority": "Medium",
                    "eligible_population": 10,
                    "evaluation_status": COMPLETED,
                    "status_reason": "",
                }
            }
        }
        controls = risk_scoring.control_summary(clean, evaluations)
        modules = risk_scoring.module_summary(clean, evaluations)
        self.assertEqual(int(controls.iloc[0].exceptions), 0)
        self.assertEqual(float(controls.iloc[0].exceptions_per_1000), 0.0)
        self.assertEqual(int(modules.iloc[0].tests_completed), 1)

    def test_not_evaluable_test_has_no_exception_rate(self) -> None:
        clean = risk_scoring.score_exceptions(exception_frame([]))
        evaluations = {
            "Example module": {
                "EX-01": {
                    "control_name": "Example test",
                    "review_priority": "Medium",
                    "eligible_population": 5,
                    "evaluation_status": NOT_EVALUABLE,
                    "status_reason": "minimum population not met",
                }
            }
        }
        controls = risk_scoring.control_summary(clean, evaluations)
        modules = risk_scoring.module_summary(clean, evaluations)
        self.assertTrue(pd.isna(controls.iloc[0].exceptions_per_1000))
        self.assertEqual(int(modules.iloc[0].tests_not_evaluable), 1)
        self.assertEqual(int(modules.iloc[0].eligible_control_evaluations), 0)

    def test_authorized_source_record_uses_supplied_metadata(self) -> None:
        directory = _case_directory("authorized_source_record")
        frames = {
            "users": pd.DataFrame([{
                "user_id": "U1", "status": "active",
                "hire_date": pd.Timestamp("2020-01-01"), "termination_date": pd.NaT,
            }])
        }
        metadata = {
            "defaults": {
                "environment": "production", "extraction_method": "approved report",
                "filter_parameters": "as of 2026-07-01", "timezone": "UTC",
                "extract_owner": "IAM owner",
            },
            "datasets": {
                "users": {
                    "source_system": "Institution IAM",
                    "query_or_report_reference": "IAM-RPT-01",
                    "expected_rows": 1,
                }
            },
        }
        record = write_source_assurance_record(
            frames, directory / "source_assurance_record.csv", metadata
        )
        self.assertEqual(record.iloc[0].source_system, "Institution IAM")
        self.assertEqual(record.iloc[0].environment, "production")
        self.assertEqual(record.iloc[0].row_count_status, "reconciled")


if __name__ == "__main__":
    unittest.main()
