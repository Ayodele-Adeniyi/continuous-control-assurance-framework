# Changelog

## 1.3.1 - 2026-07-16

- Added explicit Completed and Not Evaluable status for every control test so skipped procedures cannot appear as clean results.
- Corrected eligible populations, including the TR-04 unreconciled-item denominator, and added test-specific comparison preconditions.
- Added stable zero-exception handling and removed stale prior-run artifacts before execution.
- Required declared source metadata for institutional extracts and expanded source-data checks.
- Reframed severity as demonstration review priority and separated exceptions, deviations, and deficiencies.
- Added a 20-test practitioner catalog, expanded independent-review procedures, and increased automated boundary and negative-case coverage.
- Aligned reference SQL and documentation with the corrected implementation.
- Corrected the reproducibility lock and declared the PDF-generation dependency.

## 1.3.0 - 2026-07-16

- Added configurable data and output directories so authorized extracts can be evaluated without modifying the bundled demonstration.
- Made synthetic ground-truth labels optional while preserving labelled-condition validation when labels are supplied.
- Documented why the initial 20 controls were selected and clarified that CCAF complements rather than replaces enterprise platforms.
- Added public contribution, security, and independent-review guidance plus automated GitHub testing.
- Clarified that the current implementation runs on demand and does not claim live integration, real-time monitoring, or remediation workflow.

## 1.2.0 - 2026-07-14

- Added PA-07 for expired temporary privileged access and CM-07 for implemented changes lacking recorded preproduction testing.
- Added a source-assurance record that captures observed period, row-count, and control-total facts without claiming extract completeness.
- Expanded blocking data-quality checks for empty datasets, invalid booleans, missing temporary-access expiries, and approvals recorded after implementation.
- Added an explicit control-assurance lifecycle covering design, implementation, source reliability, operation, rollforward, and exception follow-up.
- Expanded production evidence and implementation guidance while preserving independently written language and code.

## 1.1.0 - 2026-07-14

- Replaced the unvalidated composite risk index with per-control eligible-population rates.
- Added source-data validation, SHA-256 input manifests, run metadata, and calibration records.
- Added labelled seeded conditions and automated recall/regression tests for all 18 controls.
- Corrected reconciliation aging to weekdays and documented holiday-calendar limitations.
- Externalized demonstration thresholds and review-priority weights into JSON configuration.
- Narrowed framework-mapping claims and added authoritative references.
- Added reproducible methodology-PDF generation.

## 1.0.0 - 2026-07-14

- Initial synthetic demonstration release.
