# CCAF - Continuous Control Assurance Framework

**A nonproprietary synthetic demonstration of continuous-control analytics for financial and digital-payment environments.**

Author: Ayodele Timothy Adeniyi (CISA, ACA) | Version: 1.3.1 | License: Apache-2.0

[Read the five-page CCAF methodology and validation summary](docs/CCAF_Framework_Methodology.pdf).

[Start here for independent technical review](REVIEWER_GUIDE.md).

[Use the concise independent-review response template](REVIEW_RESPONSE_TEMPLATE.md).

Repository: https://github.com/Ayodele-Adeniyi/continuous-control-assurance-framework | Version tag: https://github.com/Ayodele-Adeniyi/continuous-control-assurance-framework/tree/v1.3.1

## Purpose

CCAF is a working prototype that translates selected access, change-management, logging, reconciliation, and payment-monitoring objectives into repeatable analytics. It is designed to show how an authorized institutional team could evaluate complete supplied extracts instead of selecting row samples, rank exceptions for review, preserve run evidence, and adapt thresholds to its own systems and risk appetite.

CCAF complements rather than replaces enterprise IAM, SIEM, ITSM, GRC, ERP, fraud-monitoring, payment-monitoring, and audit-management platforms. Version 1.3.1 runs on demand against supplied extracts; it does not currently provide live connectors, scheduled execution, real-time monitoring, or remediation workflow. Those capabilities require institution-authorized integration and validation.

The repository uses seeded synthetic data and independently written documentation and code. It contains no client, employer, or production data. Version 1.3.1 is a maintenance release prepared on July 16, 2026, superseding version 1.3.0; no institutional adoption, examiner approval, external validation, or real-world performance is claimed.

## Why these 20 control tests

The 20 control tests are a bounded reference set, not a comprehensive catalog. A test was included when it:

1. addresses a recurring access, change, logging, reconciliation, or payment-integrity risk;
2. can be tested independently from structured records;
3. is transferable across institutions or technology platforms;
4. adds a distinct rule-based or comparison-based analytical pattern; and
5. can be verified with planted synthetic test conditions.

The resulting seven privileged-access, seven change/logging, and six reconciliation/payment tests demonstrate the common processing and evidence model across security, operations, and financial integrity. An adopting institution must select, modify, or add controls based on its own risk assessment, systems, policies, and obligations.

## Included components

| Component | Location | Purpose |
|---|---|---|
| Synthetic data and planted-condition labels | `src/ccaf/generate_data.py` | Generates synthetic source extracts and records the deliberately planted conditions used to verify detection |
| Twenty control tests | `src/ccaf/modules/` | Seven privileged-access, seven change/logging, and six reconciliation/payment tests |
| Data-quality validation | `src/ccaf/data_quality.py` | Checks required schemas, keys, timestamps, value types, selected relationships, and temporary-access expiry completeness before analytics run |
| Reporting and prioritization | `src/ccaf/risk_scoring.py` | Reports each test's status and eligible population and applies configurable review-priority weights |
| Audit artifacts | `src/ccaf/audit_artifacts.py` | Creates an input hash manifest, source-assurance record, calibration record, and run metadata |
| Demonstration configuration | `config/defaults.json` | Stores thresholds and weights that institutions must validate before production use |
| Reference SQL | `sql/` | Illustrative deterministic queries and feature-extraction patterns; adapt to the target database |
| Tests | `tests/test_framework.py` | Verifies reproducibility, detection of planted conditions, data-quality controls, boundaries, and weekday aging |
| Documentation | `docs/` | Methodology, governance, implementation, mapping, references, and publication checklist |
| Methodology PDF | `docs/CCAF_Framework_Methodology.pdf` | Filing-ready overview of scope, controls, validation results, implementation boundaries, and release status |

See [docs/control-test-catalog.md](docs/control-test-catalog.md) for the practitioner work program and [docs/architecture.md](docs/architecture.md) for the code map, input data contracts, and extension guide.

## Quickstart

```bash
python -m pip install -r requirements.txt
python run_all.py --regenerate
python -m unittest discover -s tests -v
```

Use `--config path/to/config.json` to supply institution-specific settings. Use `--no-charts` when running the analytics without dashboard dependencies.
Use `--data-dir path/to/authorized_extracts`, `--source-metadata path/to/source_metadata.json`, and `--output-dir path/to/run_output` to evaluate separately authorized extracts. Start with `config/source_metadata.example.json`. A `ground_truth.csv` file is optional and is used only to compare reported exceptions with known test conditions.
`requirements-lock.txt` records the exact package versions used for the Version 1.3.1 demonstration run.

## Outputs

Each successful run writes:

- `input_manifest.csv`: file names, row counts, byte counts, and SHA-256 hashes;
- `source_assurance_record.csv`: observed extract periods, row counts, and available control totals, with unresolved reconciliation fields left explicit;
- `data_quality_findings.csv`: precondition failures, if any;
- `calibration_record.csv`: effective demonstration parameters and validation status;
- `run_metadata.json`: version, runtime, configuration hash, and scoring limitation;
- exception files with control test, entity, detail, demonstration review priority, rule version, and review-priority score;
- `control_summary.csv`: status, status reason, eligible population, and exceptions per 1,000 for each test;
- `module_summary.csv`: Completed and Not Evaluable test counts plus completed-test evaluation rates, without synthetic risk tiers;
- `seeded_validation_summary.csv`: detection results for deliberately planted synthetic conditions when the corresponding label file is supplied; and
- four demonstration dashboards.

## Controls

| Module | IDs | Coverage |
|---|---|---|
| Privileged Access | PA-01 to PA-07 | Terminated access, approval, self-approval, dormancy, segregation of duties, after-hours outliers, temporary-access expiry |
| Change and Logging | CM-01 to CM-07 | Approval, segregation, emergency review, deployment traceability, log heartbeat, emergency-rate spike, preproduction test evidence |
| Reconciliation and Payments | TR-01 to TR-06 | Unmatched items, amount differences, duplicates, weekday aging, velocity outliers, threshold hovering |

## Interpretation boundaries

- Full-population language refers only to every row in the supplied in-scope extract for the covered test. It does not prove source-system completeness or eliminate other forms of audit risk.
- Planted-condition detection measures whether the code finds the conditions deliberately built into the synthetic demonstration. It is not a production accuracy rate, loss estimate, or proof of effectiveness at another institution.
- Review-priority labels and scores are transparent ordering aids. They are not confirmed deficiencies, probabilities of breach, regulatory ratings, or calibrated financial-loss measures.
- Framework mappings organize potentially relevant evidence. They do not establish compliance, satisfy an examination requirement by themselves, or imply endorsement by NIST, FFIEC, PCI SSC, or another body.
- Statistical anomalies require human review and institution-specific calibration before operational use.
- A Not Evaluable test is not a clean result and carries no exception rate.
- An automated exception is not automatically a control deviation or deficiency. A production conclusion also requires investigation, control design, implementation, source reliability, period coverage, rollforward evidence, and authorized evaluation.

See `docs/references.md` for authoritative sources and `docs/publication-checklist.md` for the steps required before claiming public dissemination.
