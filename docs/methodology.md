# CCAF Methodology

## 1. Purpose and scope

The Continuous Control Assurance Framework (CCAF) is a synthetic working prototype for selected access, change-management, logging, reconciliation, and payment-monitoring analytics. Version 1.3.1 contains 20 repeatable control tests. It evaluates supplied in-scope records, identifies conditions for review, reports the population eligible for each completed test, and preserves evidence needed to reproduce a run.

CCAF is not an identity platform, security-monitoring platform, fraud system, audit-management platform, or compliance certification tool. It does not establish that a source extract is complete, determine control effectiveness, or make remediation decisions. Its role is narrower: apply transparent tests to authorized records and give reviewers a consistent evidence package for follow-up.

## 2. Assurance context

Exception analytics are one part of a broader control-assurance process:

| Stage | Practitioner question | Evidence normally required |
|---|---|---|
| Scope and design | What risk and control requirement are being evaluated? | Risk, objective, owner, frequency, systems, period, and population |
| Implementation | Is the control configured and operating in the intended environment? | Configuration, roles, walkthrough, rule version, and environment evidence |
| Source reliability | Are the supplied records authorized, complete and accurate, and correctly filtered? | Queries or reports used to generate the extract, parameters, expected counts or totals, period coverage, and owner review |
| Execution | What procedure was performed, over what population, and with what result? | Test logic, effective configuration, evaluation status, population, and exceptions |
| Follow-up | What did investigation establish? | Reviewer, source evidence, disposition, remediation, escalation, and closure |
| Rollforward | Have changes to code, configuration, source logic, or process ownership affected consistent operation since testing? | Change history, version comparison, impact assessment, and period-end work |

CCAF supports execution and evidence organization. Production conclusions require the other stages as well.

## 3. Processing model

```text
authorized source extracts and declared source metadata
        |
        v
schema, key, timestamp, value, and relationship checks
        |
        +--> source-assurance record and input hash manifest
        v
20 versioned control tests
        |
        +--> Completed or Not Evaluable status for every test
        +--> exceptions and eligible populations for completed tests
        +--> calibration and run metadata
        +--> summaries and dashboards
        +--> seeded-condition comparison for the synthetic demonstration only
```

Critical or High data-quality findings stop the run before control tests execute. Prior CCAF outputs are cleared at the start of a run so a failed run cannot leave stale exception files that appear current.

## 4. How the tests work

The 20 tests are detective procedures documented as automated inspections or reperformances. Each catalog procedure identifies the evidence examined and the condition it is designed to determine. Bracketed terms identify institution-specific tailoring points rather than silently assuming a policy name, threshold, period, calendar, role, or source system.

Most tests apply a documented rule to each eligible record, such as identifying an active temporary privileged grant that has passed its approved expiry. Three comparison tests evaluate patterns across a supplied population:

- PA-06 compares after-hours authentication counts across active privileged users during a defined activity window.
- CM-06 compares the recent emergency-change rate with an earlier baseline.
- TR-05 compares recent transaction counts across active accounts.

Each comparison test has its own minimum conditions. A test is marked **Not Evaluable** when those conditions are not met; it is not reported as a clean zero-exception result. Exact procedures, populations, follow-up requirements, and limitations are documented in `control-test-catalog.md`.

For technical review, PA-06 and TR-05 use the median and median absolute deviation to reduce distortion from a small number of extreme values. For each value `x`, the score is `0.6745 * (x - median) / MAD`. The configured threshold is 3.0. PA-06 uses at least 30 active privileged users; TR-05 uses at least 30 active accounts. Both are Not Evaluable when the comparison has no usable variation. CM-06 does not use this formula; it applies a recent-to-baseline rate comparison and requires at least 10 recent changes, 30 baseline changes, and at least one baseline emergency change.

## 5. Evaluation statuses, populations, and rates

Every test records its status, reason, eligible population, exception count, and default review priority.

- **Completed:** the procedure ran and an exception rate may be calculated for the supplied eligible population.
- **Not Evaluable:** a required analytical condition was absent. The framework reports the reason and leaves the exception rate blank.

For a completed test:

```text
exception rate = reported exceptions / eligible population
```

Rates are shown per 1,000 eligible records or entities. Module summaries add only populations from completed tests and label the result as control-test evaluations. They are descriptive workload measures, not incident rates or institution-level risk ratings.

## 6. Source-data checks and reliability record

The pipeline checks required datasets and fields, empty extracts, primary-key completeness and uniqueness, required timestamps, boolean and numeric values, selected allowed-value sets, selected user relationships, termination dates, temporary-access expiries, and approval chronology. These checks identify obvious conditions that would make the analytics unreliable. Teams still inspect the queries or reports used to generate each extract and reconcile counts or totals to determine whether the supplied records are complete and accurate for the procedure.

For the bundled demonstration, the source-assurance record identifies the deterministic synthetic generator. When `--data-dir` points to authorized institutional extracts, `--source-metadata` is required. The supplied JSON record identifies the source system, environment, extraction method, report or query reference, filters, timezone, owner, and expected counts or totals. Expected values remain subject to independent reconciliation and approval. File hashes establish file identity after extraction; they do not establish that the extraction was complete or correctly scoped.

## 7. Configuration and review priority

Operational assumptions are externalized in `config/defaults.json` and written to `calibration_record.csv`. They include the analysis date, dormancy and activity windows, after-hours definition, comparison-population minimums, heartbeat period, change-rate comparison requirements, reconciliation aging, settlement grace, amount tolerance, approval threshold, and review-priority weights.

Critical, High, Medium, and Low are demonstration review-priority labels. They order follow-up; they are not confirmed deficiencies or institutional risk ratings. The adopting institution must approve its own thresholds, calendars, conflict matrix, priorities, and escalation service levels. Boundary testing should cover values immediately below, at, and above each applicable threshold.

## 8. Synthetic verification

The generator records deliberately planted test conditions in `data/synthetic/ground_truth.csv`. Automated tests compare the expected control/entity pairs with reported exceptions. Version 1.3.1 detects all 165 planted conditions in the fixed synthetic scenario. Three additional comparison-based observations are reported separately because an unusual synthetic observation cannot be classified as a false positive without review.

This verification demonstrates that the current code detects the conditions deliberately built into its synthetic test data. It is regression evidence, not a production accuracy rate, external validation, or proof of loss reduction. Planted-condition labels are optional for separately authorized extracts; without known labels, CCAF reports exceptions but does not calculate a planted-condition detection rate.

## 9. From exception to conclusion

CCAF uses a controlled conclusion sequence:

1. An **automated exception** means the coded condition was met.
2. An **investigated condition** means a reviewer examined supporting records and context.
3. A **confirmed deviation** means the applicable control requirement was not performed as designed.
4. A **deficiency or finding** results only after authorized personnel evaluate the confirmed deviation under the institution's methodology.

CCAF produces the first item and structures evidence for the later steps. Statistical or rule-based exceptions do not establish misconduct, control failure, or deficiency without investigation.

## 10. Limitations

- A result covers only the supplied in-scope records and the stated test.
- Production use requires authorization, field mapping, privacy review, source reconciliation, threshold approval, human review, and controlled remediation.
- PA-05 contains illustrative segregation-of-duties pairs that must be replaced or expanded using the institution's conflict matrix.
- Weekday aging does not account for federal, market, or institution-specific holidays.
- Reconciliation tests assume the supplied single-currency demonstration structure; production use must address currencies, fees, reversals, partial settlements, and product rules.
- Comparison tests require representative populations and institution-approved grouping logic.
- Reference SQL must be adapted and tested for the target database and approved configuration.
- Synthetic results do not establish adoption, supervisory acceptance, external validation, production performance, or real-world impact.
