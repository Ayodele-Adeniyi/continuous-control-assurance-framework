# CCAF Methodology

## 1. Scope

CCAF is a synthetic working prototype for selected continuous-control analytics. It evaluates every row in the supplied in-scope extracts for 20 covered tests, produces typed exception records, and preserves evidence needed to reproduce a run. It does not establish that a source extract is complete, replace professional judgment, or constitute a complete cybersecurity, fraud, compliance, or audit program.

The 20 controls are a bounded reference set rather than a comprehensive catalog. Selection required relevance to recurring access, change, logging, reconciliation, or payment-integrity risks; testability from structured records; transferability across institutions; a distinct deterministic or statistical pattern; and the ability to create labelled synthetic conditions. Adopting institutions must select, modify, or add controls based on their own risk assessments, systems, policies, and obligations.

CCAF complements rather than replaces IAM, SIEM, ITSM, GRC, ERP, fraud-monitoring, payment-monitoring, and audit-management platforms. Version 1.3.0 executes on demand against supplied extracts. Live connectors, scheduled execution, real-time monitoring, and remediation workflow are institution-authorized implementation activities, not capabilities claimed for this release.

## 2. Control-assurance lifecycle

Analytics results are only one part of a control-assurance conclusion. A production implementation should address six connected stages:

| Stage | Required question | Typical evidence |
|---|---|---|
| Scope and design | Does the control address a defined risk for the relevant systems and data? | Control objective, owner, frequency, systems, policy, and risk mapping |
| Implementation | Is the control configured and operating in the intended environment? | Configuration, access roles, code or rule version, walkthrough, and environment evidence |
| Source reliability | Are the supplied records complete, accurate, authorized, and correctly filtered? | Extraction logic, parameters, row counts, control totals, period coverage, and owner review |
| Operation | Did the control operate throughout the period and population being evaluated? | Full-population analytics, configuration history, logs, tickets, and approvals |
| Rollforward | Did code, configuration, source logic, or process ownership change after testing? | Change history, version comparison, release records, and period-end confirmation |
| Follow-up | Were exceptions investigated, resolved, or accepted by authorized personnel? | Disposition, reviewer, supporting evidence, remediation reference, and closure date |

CCAF supports selected source-reliability and operating-control procedures and creates structured exception records for follow-up. It does not independently establish source completeness, control effectiveness, or completed remediation. It can organize evidence for the other lifecycle stages, but it does not replace them.

## 3. Processing model

```text
authorized source extracts
        |
        v
schema, key, timestamp, value-type, and relationship checks
        |
        +--> source-assurance record and input hash manifest
        v
20 deterministic or statistical tests
        |
        +--> typed exceptions and per-control eligible populations
        +--> seeded-condition validation (synthetic demonstration only)
        +--> calibration and run metadata
        +--> summaries and dashboards
```

Each test is a versioned function from pandas DataFrames to an exception DataFrame and a control-specific eligible-population count. Blocking data-quality findings stop the run before exception reporting.

## 4. Detection classes

1. **Deterministic controls** express a testable condition, such as an active temporary privileged grant that has passed its approved expiry.
2. **Statistical screens** use a robust z-score based on the median and median absolute deviation to identify unusually high counts within the supplied synthetic population. The default threshold is a demonstration setting, not a claim about a universal false-positive probability.

Statistical screens identify observations for review. They do not determine intent, misconduct, or control failure without investigation.

## 5. Eligible populations and rates

Every control reports its own denominator. Examples include active privileged grants for approval tests, active temporary privileged grants for expiry tests, implemented changes for testing-evidence review, deployment records for traceability, and ledger records or active accounts for payment tests.

```text
control exception rate = reported exceptions / eligible control population
```

Rates are reported per 1,000 eligible entities. Module summaries add the denominators as **control evaluations** and report exceptions per 1,000 evaluations. The framework does not assign Low, Moderate, Elevated, or Critical module ratings because the synthetic data does not provide an empirical basis for that calibration.

## 6. Source-data assurance

The pipeline checks required datasets and fields, empty extracts, primary-key completeness and uniqueness, required timestamps, selected boolean fields, selected user relationships, termination-date completeness, temporary-access expiry completeness, and approval chronology. Findings are written to `output/data_quality_findings.csv`; Critical or High findings stop analytics execution.

The separate `source_assurance_record.csv` records observed periods, row counts, and available control totals. Expected values, extraction ownership, and reviewer approval remain unresolved in the demonstration. A production team must reconcile those fields to independent source evidence. Hashes prove file identity after extraction; they do not prove that the extraction was complete or correctly filtered.

## 7. Configuration and boundary testing

| Parameter | Default | Required production action |
|---|---:|---|
| Dormant privileged access | 60 calendar days | Align to access policy and recertification cadence |
| Temporary-access grace | 0 hours | Align to approved emergency or break-glass procedure |
| After-hours window | 22:00-05:59 | Apply local timezone, maintenance windows, and role context |
| Robust z-score | 3.0 | Back-test against labelled institutional outcomes |
| Log heartbeat | 24 hours | Align to source criticality and expected event cadence |
| Reconciliation aging | 5 weekdays | Replace weekday approximation with the institution's holiday calendar |
| Approval limit | 10,000 currency units | Replace with the applicable authorization matrix |
| Threshold-hover band | 97%-99.9%, at least 3 events | Validate against product, customer, and transaction context |

All defaults are externalized in `config/defaults.json` and recorded in `output/calibration_record.csv`. Production testing should include values immediately below, at, and above each applicable boundary, and should confirm that the effective configuration matches the approved configuration.

## 8. Synthetic validation

The generator records each deliberately injected condition in `data/synthetic/ground_truth.csv`. Automated tests compare unique control/entity pairs against reported exceptions. Version 1.3.0 detects every deliberately seeded condition in the fixed synthetic scenario. Additional statistical exceptions can occur because the background synthetic population may also satisfy an outlier rule; those observations are reported separately rather than labelled false positives without adjudication. Ground-truth labels are optional for separately authorized extracts; without labels, CCAF reports exceptions but does not calculate recall.

## 9. Limitations

- Production deployment requires authorized data, field mapping, privacy review, extraction reconciliation, threshold calibration, and human triage.
- A full-population result covers only the supplied in-scope extract and covered test.
- Weekday aging does not account for federal, market, or institution-specific holidays.
- Statistical baselines require sufficient and representative observations.
- A result does not establish operating effectiveness without design, implementation, period coverage, rollforward, and follow-up evidence.
- CCAF supplements rather than replaces vulnerability management, penetration testing, fraud investigation, incident response, and judgment-based audit procedures.
- Demonstration results do not establish adoption, external validation, supervisory acceptance, or real-world loss reduction.
