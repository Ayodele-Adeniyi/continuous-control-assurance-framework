# CCAF - Continuous Control Assurance Framework

**A nonproprietary synthetic demonstration of continuous-control analytics for financial and digital-payment environments.**

Author: Ayodele Timothy Adeniyi (CISA, ACA) | Version: 1.3.1 | License: Apache-2.0

Release record: [v1.3.1](https://github.com/Ayodele-Adeniyi/continuous-control-assurance-framework/tree/v1.3.1), prepared July 16, 2026, supersedes v1.3.0. See the [changelog](CHANGELOG.md).

## Start here

- **Practitioners:** read the concise [methodology and validation summary](docs/CCAF_Framework_Methodology.pdf) and [control-test catalog](docs/CCAF_Control_Test_Catalog.pdf).
- **Independent reviewers:** begin with those two PDFs and the [review guide](REVIEWER_GUIDE.md). A documents-based design review is sufficient; source-code inspection and local reproduction are optional.
- **Contributors:** see [CONTRIBUTING.md](CONTRIBUTING.md).

Repository: https://github.com/Ayodele-Adeniyi/continuous-control-assurance-framework

## Purpose

CCAF is a working prototype that translates selected access, change-management, logging, reconciliation, and payment-monitoring objectives into repeatable analytics. It is designed to show how an authorized institutional team could evaluate complete supplied extracts instead of selecting row samples, rank exceptions for review, preserve run evidence, and adapt thresholds to its own systems and risk appetite.

CCAF complements rather than replaces enterprise IAM, SIEM, ITSM, GRC, ERP, fraud-monitoring, payment-monitoring, and audit-management platforms. Version 1.3.1 runs on demand against supplied extracts; it does not currently provide live connectors, scheduled execution, real-time monitoring, or remediation workflow. Those capabilities require institution-authorized integration and validation.

The repository uses seeded synthetic data and independently written documentation and code. It contains no client, employer, or production data. No institutional adoption, examiner approval, external validation, or real-world performance is claimed.

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
| Reviewer response form | `docs/CCAF_Independent_Review_Response_Template.docx` | Concise one-page Word form generated from the four focused prompts in `REVIEW_RESPONSE_TEMPLATE.md` |

See [docs/control-test-catalog.md](docs/control-test-catalog.md) for the practitioner work program and [docs/architecture.md](docs/architecture.md) for the code map, input data contracts, and extension guide.

## Quickstart

```bash
python -m pip install -r requirements.txt
python run_all.py --regenerate --seed 42
python -m unittest discover -s tests -v
```

- Seed `42` is the official release benchmark. Use another integer with `--seed` to generate a different reproducible exploratory synthetic population; exploratory results are not the documented release benchmark.
- Use `--config path/to/config.json` to supply institution-specific settings.
- Use `--data-dir path/to/authorized_extracts`, `--source-metadata path/to/source_metadata.json`, and `--output-dir path/to/run_output` to evaluate separately authorized extracts. Start with `config/source_metadata.example.json`.
- Use `--no-charts` when running the analytics without dashboard dependencies.
- A `ground_truth.csv` file is optional and is used only to compare reported exceptions with known test conditions.

`requirements-lock.txt` records the exact package versions used for the Version 1.3.1 demonstration run.

## Independent review package

The normal review package consists of the five-page methodology PDF, the control-test catalog PDF, the concise response form, and this guide. These materials support a professional design review without requiring the reviewer to install software. The public repository is available when a reviewer independently chooses to inspect code, output artifacts, or reproduce the demonstration.

## Outputs

Each successful run writes:

- `input_manifest.csv`: file names, row counts, byte counts, and SHA-256 hashes;
- `source_assurance_record.csv`: observed extract periods, row counts, and available control totals, with unresolved reconciliation fields left explicit;
- `data_quality_findings.csv`: precondition failures, if any;
- `calibration_record.csv`: effective demonstration parameters and validation status;
- `run_metadata.json`: version, runtime, configuration hash, synthetic seed and benchmark status when applicable, and scoring limitation;
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

- The repository contains seeded synthetic data and independently written documentation and code; no employer, client, or production material was used.
- The documented release result describes the official seed-42 benchmark. Exploratory seeds produce separate reproducible synthetic results; in both modes, full-population means every row of the supplied in-scope extract, and detection of planted conditions is regression evidence, not a production accuracy rate.
- The 20 tests are a bounded reference set, not a comprehensive catalog, and complement rather than replace enterprise security, GRC, and audit platforms.
- No institutional adoption, external validation, or endorsement by any referenced organization is claimed.

See `docs/references.md` for authoritative sources and `docs/publication-checklist.md` for the steps required before claiming public dissemination.
