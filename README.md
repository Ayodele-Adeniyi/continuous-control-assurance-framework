# CCAF - Continuous Control Assurance Framework

**A nonproprietary synthetic demonstration of continuous-control analytics for financial and digital-payment environments.**

Author: Ayodele Timothy Adeniyi (CISA, ACA) | Version: 1.3.0 | License: Apache-2.0

[Read the five-page CCAF methodology and validation summary](docs/CCAF_Framework_Methodology.pdf).

Repository: https://github.com/Ayodele-Adeniyi/continuous-control-assurance-framework | Version tag: https://github.com/Ayodele-Adeniyi/continuous-control-assurance-framework/tree/v1.3.0

## Purpose

CCAF is a working prototype that translates selected access, change-management, logging, reconciliation, and payment-monitoring objectives into repeatable analytics. It is designed to show how an authorized institutional team could evaluate complete supplied extracts instead of selecting row samples, rank exceptions for review, preserve run evidence, and adapt thresholds to its own systems and risk appetite.

CCAF complements rather than replaces enterprise IAM, SIEM, ITSM, GRC, ERP, fraud-monitoring, payment-monitoring, and audit-management platforms. Version 1.3.0 runs on demand against supplied extracts; it does not currently provide live connectors, scheduled execution, real-time monitoring, or remediation workflow. Those capabilities require institution-authorized integration and validation.

The repository uses seeded synthetic data and independently written code. It contains no client, employer, or production data. Version 1.3.0 was publicly released on July 16, 2026; no institutional adoption, examiner approval, external validation, or real-world performance is claimed.

## Why these 20 controls

The 20 controls are a bounded reference set, not a comprehensive catalog. A control was included when it:

1. addresses a recurring access, change, logging, reconciliation, or payment-integrity risk;
2. can be tested independently from structured records;
3. is transferable across institutions or technology platforms;
4. adds a distinct deterministic or statistical analytical pattern; and
5. can be validated with labelled synthetic conditions.

The resulting seven privileged-access, seven change/logging, and six reconciliation/payment tests demonstrate the common processing and evidence model across security, operations, and financial integrity. An adopting institution must select, modify, or add controls based on its own risk assessment, systems, policies, and obligations.

## Included components

| Component | Location | Purpose |
|---|---|---|
| Seeded data and labels | `src/ccaf/generate_data.py` | Generates synthetic source extracts and a ground-truth file for deliberately injected conditions |
| Twenty controls | `src/ccaf/modules/` | Seven privileged-access, seven change/logging, and six reconciliation/payment tests |
| Data-quality validation | `src/ccaf/data_quality.py` | Checks required schemas, keys, timestamps, value types, selected relationships, and temporary-access expiry completeness before analytics run |
| Reporting and prioritization | `src/ccaf/risk_scoring.py` | Reports each control against its eligible population and applies configurable review-priority weights |
| Audit artifacts | `src/ccaf/audit_artifacts.py` | Creates an input hash manifest, source-assurance record, calibration record, and run metadata |
| Demonstration configuration | `config/defaults.json` | Stores thresholds and weights that institutions must validate before production use |
| Reference SQL | `sql/` | Illustrative deterministic queries and feature-extraction patterns; adapt to the target database |
| Tests | `tests/test_framework.py` | Verifies reproducibility, seeded-condition recall, data-quality controls, and weekday aging |
| Documentation | `docs/` | Methodology, governance, implementation, mapping, references, and publication checklist |
| Methodology PDF | `docs/CCAF_Framework_Methodology.pdf` | Filing-ready overview of scope, controls, validation results, implementation boundaries, and release status |

See [docs/architecture.md](docs/architecture.md) for the code map, input data contracts, and extension guide.

## Quickstart

```bash
python -m pip install -r requirements.txt
python run_all.py --regenerate
python -m unittest discover -s tests -v
```

Use `--config path/to/config.json` to supply institution-specific settings. Use `--no-charts` when running the analytics without dashboard dependencies.
Use `--data-dir path/to/authorized_extracts` and `--output-dir path/to/run_output` to evaluate a separately authorized set of extracts without modifying the bundled demonstration. A `ground_truth.csv` file is optional and is used only to calculate labelled-condition recall when known labels exist.
`requirements-lock.txt` records the exact package versions used for the version 1.3.0 demonstration run.

## Outputs

Each successful run writes:

- `input_manifest.csv`: file names, row counts, byte counts, and SHA-256 hashes;
- `source_assurance_record.csv`: observed extract periods, row counts, and available control totals, with unresolved reconciliation fields left explicit;
- `data_quality_findings.csv`: precondition failures, if any;
- `calibration_record.csv`: effective demonstration parameters and validation status;
- `run_metadata.json`: version, runtime, configuration hash, and scoring limitation;
- exception files with control, entity, detail, severity, rule version, and review-priority score;
- `control_summary.csv`: exceptions per 1,000 eligible entities for each control;
- `risk_summary.csv`: module-level control evaluations and exception rates, without synthetic risk tiers;
- `seeded_validation_summary.csv`: recall of deliberately injected synthetic conditions when a ground-truth file is supplied; and
- four demonstration dashboards.

## Controls

| Module | IDs | Coverage |
|---|---|---|
| Privileged Access | PA-01 to PA-07 | Terminated access, approval, self-approval, dormancy, segregation of duties, after-hours outliers, temporary-access expiry |
| Change and Logging | CM-01 to CM-07 | Approval, segregation, emergency review, deployment traceability, log heartbeat, emergency-rate spike, preproduction test evidence |
| Reconciliation and Payments | TR-01 to TR-06 | Unmatched items, amount differences, duplicates, weekday aging, velocity outliers, threshold hovering |

## Interpretation boundaries

- Full-population language refers only to every row in the supplied in-scope extract for the covered test. It does not prove source-system completeness or eliminate other forms of audit risk.
- Seeded-condition recall measures whether the code finds deliberately injected synthetic conditions. It is not a production false-positive rate, loss estimate, or proof of effectiveness at another institution.
- Review-priority scores are transparent ordering aids. They are not probabilities of breach, regulatory ratings, or calibrated financial-loss measures.
- Framework mappings organize potentially relevant evidence. They do not establish compliance, satisfy an examination requirement by themselves, or imply endorsement by NIST, FFIEC, PCI SSC, or another body.
- Statistical anomalies require human review and institution-specific calibration before operational use.
- Exception analytics are one part of control assurance. A production conclusion on operating effectiveness also requires control design, implementation, source reliability, period coverage, change/rollforward evidence, and documented exception follow-up.

See `docs/references.md` for authoritative sources and `docs/publication-checklist.md` for the steps required before claiming public dissemination.
