# Governance, Evidence, and Responsible Use

## Run evidence

Each run creates:

1. an input manifest with file names, row counts, byte counts, and SHA-256 hashes;
2. a source-assurance record showing observed period, row-count, and control-total facts while leaving independent reconciliation fields explicit;
3. a data-quality report generated before control analytics;
4. typed exception files with rule version and detection date;
5. control and module summaries using documented eligible populations;
6. a calibration record showing that bundled values are demonstration defaults;
7. run metadata containing the framework version and effective configuration hash; and
8. seeded-condition validation for the synthetic demonstration.

Institutions should retain these artifacts according to an approved records schedule. Exception files inherit the classification of their most sensitive source field.

## Minimum production evidence

| Evidence area | Minimum record |
|---|---|
| Scope | Control objective, risk addressed, systems, period, population, owner, and reviewer |
| Extraction | Source, query or report reference, parameters, timezone, extract date, row count, and control total |
| Completeness and accuracy | Independent expected count or total, reconciliation result, unresolved difference, and approval |
| Environment | Production or nonproduction status and evidence that relevant code and configuration are equivalent |
| Configuration | Effective threshold, tolerance, calendar, role mapping, approval limit, and configuration hash |
| Change history | Relevant changes to source logic, rules, systems, roles, or configurations during the period |
| Exception review | Reviewer, disposition, evidence, remediation reference, escalation, and closure date |

An input hash demonstrates that a reviewed file has not changed. It does not establish that the source system produced every required record or that the extraction parameters were correct.

## Rollforward and revalidation

Revalidate a control after a material change to source-system logic, interface design, field mapping, access model, deployment process, threshold, calendar, or analytics code. If testing occurred before period end, document whether relevant changes occurred after the test date and perform additional work where needed.

When a nonproduction environment is used for configuration or boundary testing, confirm and retain evidence that relevant code and configuration match production. Do not infer equivalence from naming conventions alone.

## Remediation workflow

| Demonstration severity | Suggested initial triage | Required institutional decision |
|---|---|---|
| Critical | Same business day | Confirm owner, urgency, and escalation path |
| High | Within 3 business days | Determine cause and remediation plan |
| Medium | Within 10 business days | Review in batch and monitor recurrence |
| Low | Next review cycle | Aggregate and trend |

These periods are examples, not regulatory requirements. The adopting institution must approve its own service levels.

Close each exception as confirmed issue, non-issue, accepted risk, duplicate, or another documented disposition. Preserve the reviewer, date, supporting evidence, and remediation reference. Use adjudicated results to recalibrate rules.

## Responsible use

- Run CCAF only on institution-authorized data under applicable privacy, security, and data-governance requirements.
- Statistical anomalies require human review and do not establish misconduct.
- Separate manual and automated components when one control depends on both.
- Do not publish client-identifying, employee-identifying, or production data.
- Do not represent framework mappings as certifications, examination findings, or agency endorsements.
- Treat the bundled thresholds and weights as unvalidated demonstration settings.

## Provenance

The repository contains seeded synthetic data, independently written language, and independently written code. No source workbook, employer template, client record, or production material is included. The Apache-2.0 license permits study and adaptation, subject to its terms.
