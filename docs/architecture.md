# CCAF Architecture

This document explains how CCAF is put together: where it sits relative to institutional systems, how a run flows through the code, what each layer is responsible for, the input and output data contracts, and how to extend the framework with a new control test. It is supplemental architecture documentation for Version 1.3.1.

## 1. Context: where CCAF sits

```text
   IAM / directory      ITSM / CI-CD        core banking /
   (users, grants,      (changes,           payment processor
    authentications)     deployments)       (ledger, settlement)
         |                    |                    |
         |   authorized, read-only extracts        |
         +-----------------+--+--------------------+
                           |
                           v
                    +-------------+
                    |    CCAF     |   independent control-assurance
                    | (this repo) |   analytics over system outputs
                    +-------------+
                           |
                           v
        evaluation statuses, exceptions, rates, evidence artifacts, dashboards
        (consumed by audit, risk, and compliance reviewers)
```

Version 1.3.1 does not administer controls, hold credentials, or connect to live systems. It consumes authorized extracts that upstream platforms (IAM, SIEM, ITSM, GRC, ERP, and payment systems) already produce, applies independent analytics to selected indicators of control operation, and flags conditions for review. It does not, by itself, determine control operating effectiveness. Its outputs are review artifacts and exception indicators, not conclusions on operating effectiveness or remediation actions.

## 2. Runtime pipeline

The end-to-end data flow is described in `methodology.md` section 3. In brief: extracts are loaded, data-quality preconditions are checked (Critical or High findings stop the run), the 20 control tests record Completed or Not Evaluable status, and the run emits structured exception records, rates for completed tests, provenance artifacts, optional seeded-condition comparison, and dashboards.

## 3. Code map

```text
run_all.py                    orchestration and CLI
config/defaults.json          demonstration thresholds and weights
src/ccaf/
  config.py                   loads configuration and checks required sections
  generate_data.py            synthetic extracts + planted-condition labels
  data_quality.py             precondition checks; blocks unreliable runs
  modules/
    privileged_access.py      PA-01 .. PA-07
    change_logging.py         CM-01 .. CM-07
    reconciliation.py         TR-01 .. TR-06
  results.py                  stable exception schema and evaluation-status contract
  risk_scoring.py             review-priority scores; control-test and module summaries
  audit_artifacts.py          input hashes, source-assurance, calibration, run metadata
  validation.py               planted-condition detection (when labels are supplied)
tests/test_framework.py       reproducibility, detection, data-quality, boundary, and date-logic tests
sql/                          illustrative deterministic queries (adapt per database)
scripts/                      methodology-PDF builder
```

Responsibilities per layer:

| Layer | Responsibility | Deliberately does not |
| --- | --- | --- |
| `run_all.py` | Parse CLI flags (`--regenerate`, `--config`, `--data-dir`, `--output-dir`, `--no-charts`), sequence the layers, render dashboards | Contain control logic |
| `config.py` | Load JSON configuration and verify that required top-level sections are present | Hard-code thresholds |
| `data_quality.py` | Validate schemas, keys, timestamps, value types, selected relationships, and approval chronology before analytics run | Silently repair data |
| `modules/*` | Implement control tests as pure functions | Read files, write files, or mutate inputs |
| `results.py` | Define stable exception and evaluation-status contracts | Interpret results |
| `risk_scoring.py` | Apply configurable review weights and report completed-test rates | Assign risk tiers or loss estimates |
| `audit_artifacts.py` | Preserve reproducibility evidence for the run | Interpret results |
| `validation.py` | Compare exceptions against supplied planted-condition labels | Claim production accuracy |

## 4. The module contract

Every analytics module exposes the same interface:

```python
run(<input frames>, as_of: pd.Timestamp, config: dict)
    -> (exceptions: pd.DataFrame, evaluations: dict[str, dict])
```

Rules of the contract:

1. Modules are pure: no file I/O, no global state, inputs are not mutated.
2. Every exception record carries `module`, `control_id`, `control_name`, `review_priority`, `entity_id`, `detail`, `exposure_factor` (clipped to 1.0-2.0 downstream), and `rule_version`.
3. `evaluations` maps every control ID to its name, demonstration review priority, eligible population, `Completed` or `Not Evaluable` status, and status reason.
4. Per-1,000 rates are calculated only for Completed tests. A Not Evaluable test retains its observed population and reason but has no exception rate.
5. Operational thresholds exposed by Version 1.3.1 come from configuration; control-test definitions, review-priority assignments, and rule logic remain versioned code.
6. `RULE_VERSION` is stamped on every exception so results remain attributable as logic evolves.

`run_all.run_modules()` calls each module, concatenates exceptions using a stable schema that also supports clean runs, assigns sequential `exception_id` values and `detected_at`, and passes the evaluation records to `risk_scoring`.

## 5. Input data contracts

Eight extracts (plus one optional label file) form the input schema. Timestamps are parsed as naive datetimes; institutions must normalize time zones during mapping. Column names are the mapping target for `--data-dir` use. Institutional extracts also require `--source-metadata` using `config/source_metadata.example.json`; the declared record prevents production evidence from being mislabeled as synthetic and preserves source, scope, owner, and reconciliation information.

### users.csv
| Field | Type | Meaning | Consumed by |
| --- | --- | --- | --- |
| user_id | string, unique | Person identifier; join key | all PA tests (via join) |
| name, department, hire_date | string / date | Context for reviewers | none (context) |
| status | `active` / `terminated` | Employment state | PA-01, PA-04 scope |
| termination_date | date, blank if active | Separation date | PA-01 aging |

### access_grants.csv
| Field | Type | Meaning | Consumed by |
| --- | --- | --- | --- |
| grant_id | string, unique | Grant identifier; exception entity | PA-01, PA-02, PA-03, PA-07 |
| user_id | string | Grantee | joins |
| entitlement | string | Permission name | PA-05 conflict pairs |
| privileged | boolean | Elevated-permission flag | scope for PA-01, PA-02, PA-04, PA-06, PA-07 |
| granted_at | timestamp | Provisioning time | context |
| approved_by | string, may be blank | Approver user_id | PA-02 (blank), PA-03 (equals user_id) |
| grant_status | `active` / `revoked` | Current state | scope (active only) |
| temporary | boolean | Time-boxed grant flag | PA-07 scope |
| expires_at | timestamp, blank unless temporary | Approved expiry | PA-07 |

### auth_logs.csv
| Field | Type | Meaning | Consumed by |
| --- | --- | --- | --- |
| event_id | string, unique | Event identifier | key checks |
| user_id | string | Authenticating user | PA-04, PA-06 |
| system | string | Target system | context |
| timestamp | timestamp | Event time | PA-04 recency, PA-06 night hours |
| success | boolean | Authentication outcome | PA-04 and PA-06 count successes only |

### changes.csv
| Field | Type | Meaning | Consumed by |
| --- | --- | --- | --- |
| change_id | string, unique | Change record; exception entity | CM-01, CM-02, CM-03, CM-07; CM-04 join |
| system | string | Affected system | detail text |
| category | `standard` / `normal` / `major` | Change class | exposure in CM-01, CM-07 |
| requested_by | string | Requester | context |
| approved_by | string, may be blank | Approver | CM-01 (blank), CM-02 (equals implementer) |
| implemented_by | string | Implementer | CM-02 |
| approved_at | timestamp | Approval time | data-quality chronology check |
| implemented_at | timestamp | Implementation time | CM-06 windowing |
| emergency | boolean | Emergency flag | CM-03 scope, CM-06 rates |
| pir_completed | boolean | Post-implementation review done | CM-03 |
| test_completed | boolean | Preproduction test done | CM-07 |
| test_approved_by | string, may be blank | Test approver | CM-07 |
| status | string | Record state | context |

### deploy_logs.csv
| Field | Type | Meaning | Consumed by |
| --- | --- | --- | --- |
| deploy_id | string, unique | Deployment event; exception entity | CM-04 |
| system | string | Target system | detail text |
| deployed_at | timestamp | Deployment time | context |
| change_id | string, may be blank | Referenced change record | CM-04 (blank or unknown) |

### log_heartbeats.csv
| Field | Type | Meaning | Consumed by |
| --- | --- | --- | --- |
| source_id | string, unique | Log source; exception entity | CM-05 |
| system, log_source | string | Source identity | detail text |
| last_event_at | timestamp | Most recent event received | CM-05 quiet hours |

### ledger.csv
| Field | Type | Meaning | Consumed by |
| --- | --- | --- | --- |
| ledger_row_id | string, unique | Posting identity (distinct from txn_id) | key checks |
| txn_id | string | Transaction identifier | TR-01 join, TR-03 duplicates |
| account_id | string | Account | TR-05, TR-06 grouping |
| amount | decimal | Posted amount | TR-02 compare, TR-06 band, value exposure |
| currency | string | Currency code | context (single-currency demonstration) |
| booked_at | timestamp | Booking date | TR-04 aging, TR-05 window |
| reconciled | boolean | Cleared flag | TR-04 scope |

### processor_settlement.csv
| Field | Type | Meaning | Consumed by |
| --- | --- | --- | --- |
| settlement_row_id | string, unique | Settlement record identity | key checks |
| txn_id | string | Transaction identifier | TR-01, TR-02 join |
| settle_amount | decimal | Settled amount | TR-02 |
| settled_at | timestamp | Settlement date | context |

### ground_truth.csv (optional)
| Field | Meaning |
| --- | --- |
| injection_id | Label identifier |
| control_id | Control expected to detect the condition |
| entity_id | Entity carrying the seeded condition |
| description | Human-readable description |

Supplied only for labelled synthetic data; enables `seeded_validation_summary.csv`. Never applicable to production extracts.

## 6. Output contract

Run artifacts and their meaning are listed in the README (Outputs section). The exception schema adds two orchestration fields to the module contract fields: `exception_id` (sequential per run) and `detected_at` (the configured as-of time), plus `review_priority_score` from `risk_scoring.py`. `control_summary.csv` preserves each test's evaluation status and reason. `module_summary.csv` separately counts Completed and Not Evaluable tests.

## 7. Configuration reference

`config/defaults.json` holds demonstration values that institutions must validate before any operational use:

| Section | Keys | Used by |
| --- | --- | --- |
| top level | `as_of` | all date arithmetic |
| `privileged_access` | `dormancy_days`, `activity_window_days`, `minimum_comparison_population`, `night_hours`, `robust_z_threshold`, `temporary_access_grace_hours` | PA-04, PA-06, PA-07 |
| `change_logging` | `heartbeat_hours`, `emergency_spike_factor`, `recent_window_days`, `minimum_recent_changes`, `minimum_baseline_changes` | CM-05, CM-06 |
| `reconciliation` | `aging_business_days`, `robust_z_threshold`, `approval_limit`, `hover_low`, `hover_high`, `hover_min_count`, `amount_tolerance`, `recent_window_days`, `minimum_comparison_population`, `settlement_grace_days` | TR-01, TR-02, TR-04, TR-05, TR-06 |
| `scoring` | `review_priority_weights` (Critical/High/Medium/Low) | review-priority scores |

Every effective value is written to `calibration_record.csv` on each run.

## 8. Adding a control

1. **Specify it** using the proposal structure in `CONTRIBUTING.md` (risk, population, logic, limitations, labelled condition and negative case, exception schema, cautious traceability).
2. **Implement it** in the appropriate module under `src/ccaf/modules/`, following the module contract in section 4. A new domain gets a new module file exposing the same `run()` signature.
3. **Register its evaluation** in the module's `evaluations` dict, including population, status, reason, name, and demonstration review priority. A Completed test reports a rate even at zero exceptions; a Not Evaluable test does not.
4. **Add configuration keys** to the module's section in `config/defaults.json`; do not hard-code thresholds.
5. **Plant it** in `generate_data.py`: add the condition at a controlled rate and record it with a `_truth()` label so the synthetic verification covers it. Include a negative case that must not alert.
6. **Wire new inputs**, if any: add the dataset to `REQUIRED_DATE_COLUMNS` (or `OPTIONAL_DATE_COLUMNS`) in `run_all.py` and add schema checks in `data_quality.py`.
7. **Test it** in `tests/test_framework.py` (detection, negative case, and any date or boundary logic).
8. **Document it**: README control table, `framework-mapping.md` row with interpretive boundary, an illustrative query in `sql/` if a deterministic pattern exists, and a CHANGELOG entry. Bump `RULE_VERSION` in the touched module.

## 9. Design decisions

- **Pure-function modules** keep control logic testable and portable; all I/O lives at the edges (`run_all.py`, `audit_artifacts.py`).
- **Per-test evaluation records** replace implicit execution assumptions so a skipped procedure cannot appear to be a clean result.
- **Per-test eligible populations** replace a composite risk index so every reported rate has a transparent denominator.
- **Fail-closed data quality**: unreliable extracts stop the run rather than produce plausible-looking exceptions, because absence of alerts must be as trustworthy as their presence.
- **Configuration over code** for exposed operational thresholds, so institutional calibration of those values does not require editing analytics logic.
- **Versioned rules and hashed inputs** make any historical exception reproducible and attributable to the exact logic and data that produced it.

For methodology, scoring, and limitations, see [methodology.md](methodology.md). For review procedures, see [REVIEWER_GUIDE.md](../REVIEWER_GUIDE.md).
