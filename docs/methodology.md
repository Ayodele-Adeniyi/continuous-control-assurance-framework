# CCAF Methodology

## 1. What CCAF is

The Continuous Control Assurance Framework (CCAF) is a synthetic working prototype for continuous-control analytics. Version 1.3.1 contains 20 repeatable control tests covering privileged access, change management, logging, reconciliation, and payment monitoring. Given a set of authorized extracts, it evaluates the supplied in-scope records, identifies conditions for review, reports the population eligible for each completed test, and preserves the evidence needed to reproduce the run.

CCAF addresses a specific part of the assurance process: applying transparent tests consistently across supplied records and organizing the resulting evidence for follow-up. It is not an identity platform, security-monitoring platform, fraud system, audit-management platform, or compliance certification tool. It does not establish that a source extract is complete, determine control effectiveness, or make remediation decisions.

The sections below follow the assurance work in order: how records move through the framework, how the tests operate, what the results mean, how the demonstration is verified, and what an institution must do before using the framework with authorized records.

## 2. How CCAF works

CCAF uses four connected layers. Each layer has a defined responsibility and produces evidence for the next stage without replacing the professional judgment that follows automated testing.

| Layer | Primary responsibility | Output or decision |
|---|---|---|
| Data and source assurance | Receive authorized extracts and declared source metadata; check required files, fields, keys, timestamps, values, and selected relationships. | Data-quality findings, source-assurance record, and input hash manifest. Critical or High findings stop the run. |
| Control testing | Apply 20 versioned rule-based and comparison procedures to the eligible records using the approved configuration. | Completed or Not Evaluable status for every test, eligible populations, and structured exceptions. |
| Evidence and traceability | Preserve the rule version, configuration, calibration, source-file identity, summaries, and run metadata. | A reproducible evidence bundle showing what was supplied, what was tested, and what was reported. |
| Professional review | Investigate reported conditions and assess them against the institution's control requirements and methodology. | Disposition, remediation, escalation, or a formal conclusion by authorized personnel; CCAF does not make this conclusion. |

The resulting flow is:

```text
authorized records and declared source metadata
        |
        v
data-quality and source-assurance checks
        |
        v
scoping and institution-approved configuration
        |
        v
20 versioned control procedures across three modules
        |
        v
evaluation status, eligible populations, and structured exceptions
        |
        v
evidence bundle, run metadata, and integrity manifest
        |
        v
professional investigation and institutional conclusion
```

### Reliability guardrails

Before testing, CCAF checks the structure and basic integrity of the supplied records; Critical or High findings stop the run. When required evidence or analytical conditions are absent, the affected procedure is reported as **Not Evaluable**, never as a clean result. The framework also records the settings, rule versions, source-file identities, eligible populations, and exceptions used in each completed procedure. These safeguards support review and reproducibility, but the practitioner must still establish source completeness and accuracy and approve institution-specific settings. File hashes preserve file identity after extraction; they do not prove that an extract was complete or correctly scoped.

## 3. How the tests operate

All 20 tests are detective procedures documented as automated inspections or reperformances. Each entry in `control-test-catalog.md` states the risk, intended control condition, records examined, automated procedure, evidence required for follow-up, and institution-specific tailoring points. Bracketed terms identify items an adopting institution must define, such as a policy, threshold, period, calendar, role, conflict matrix, or source system.

Most tests apply a documented rule to each eligible record. One example is identifying an active temporary privileged grant that has passed its approved expiry. Three tests instead compare activity across a supplied population:

- PA-06 compares after-hours authentication counts across active privileged users during a defined activity window.
- CM-06 compares the recent emergency-change rate with an earlier baseline.
- TR-05 compares recent transaction counts across active accounts.

Each comparison test has minimum analytical conditions. When those conditions are absent, the test is marked **Not Evaluable** rather than reported as a clean zero-exception result. Exact procedures, populations, follow-up requirements, and limitations for every test are documented in `control-test-catalog.md`.

### Technical specification for comparison tests

PA-06 and TR-05 use the median and median absolute deviation so a small number of extreme values do not distort the comparison baseline. For each value `x`, the score is:

```text
0.6745 * (x - median) / MAD
```

The configured threshold is 3.0. PA-06 requires at least 30 active privileged users and TR-05 requires at least 30 active accounts. Both tests are Not Evaluable when the comparison has no usable variation. CM-06 does not use this formula. It applies a recent-to-baseline rate comparison and requires at least 10 recent changes, 30 baseline changes, and one baseline emergency change.

## 4. What the results mean

Every test records its status, the reason for that status, its eligible population, its exception count, and a default review priority.

- **Completed:** The procedure ran, and an exception rate may be calculated for the supplied eligible population.
- **Not Evaluable:** A required analytical condition was absent. The framework reports the reason and leaves the exception rate blank.

For a completed test, the rate is directly recomputable:

```text
exception rate = reported exceptions / eligible population
```

Rates are shown per 1,000 eligible records or entities so each result carries its own population context. Module summaries add only the populations of completed tests and label the result as control-test evaluations. These are descriptive measures for planning and prioritizing review work. They are not incident rates, institution-level risk ratings, or conclusions about control effectiveness.

Critical, High, Medium, and Low are demonstration review-priority labels. They order follow-up work; they are not confirmed deficiencies or institutional risk ratings. The review-priority score combines a configurable priority weight with an exposure factor bounded from 1.0 to 2.0. It is not a loss probability, compliance rating, or empirically calibrated risk score.

## 5. How the demonstration is verified

The synthetic demonstration includes a known answer key. The data generator deliberately plants test conditions and records them in `data/synthetic/ground_truth.csv`. Automated regression tests then compare the expected control-and-entity pairs with the exceptions reported by the run.

Version 1.3.1 detects all 165 planted conditions in the official fixed seed-42 scenario. Three additional comparison-based observations are reported separately because an unusual synthetic observation cannot be classified as an error or false positive without review. The browser workspace reproduces this fixed documented demonstration so reviewers can execute the framework and inspect the resulting evidence without installing software locally.

This verification shows that the current code detects the conditions deliberately built into its synthetic test data. It is regression evidence, not a production accuracy rate, external validation, or proof of loss reduction. Planted-condition labels are optional for separately authorized extracts. Without known labels, CCAF reports exceptions but does not calculate a planted-condition detection rate.

## 6. Running CCAF on institutional data

The bundled demonstration uses reproducible synthetic data. Seed 42 defines the official release benchmark; another integer produces a different exploratory population that can be regenerated with the same seed. Using separately authorized institutional extracts adds two responsibilities: establishing that the supplied records are reliable for each procedure and approving the configuration used for the run.

### Establishing source reliability

The pipeline checks required datasets and fields, empty extracts, primary-key completeness and uniqueness, required timestamps, boolean and numeric values, selected allowed-value sets, selected user relationships, termination dates, temporary-access expiries, and approval chronology. These checks identify obvious conditions that would make the analytics unreliable, but they cannot prove that an extract is complete and accurate.

Teams must still inspect the queries or reports used to generate each extract and reconcile expected counts or totals to determine whether the supplied records are complete and accurate for the procedure. When `--data-dir` points to institutional extracts, `--source-metadata` is required. The supplied JSON record identifies the source system, environment, extraction method, report or query reference, filters, timezone, owner, and expected counts or totals. Expected values remain subject to independent reconciliation and approval. File hashes establish file identity after extraction; they do not establish that the extraction was complete or correctly scoped.

### Approving configuration

Operational assumptions are externalized in `config/defaults.json` and written to `calibration_record.csv` on each run. They include the analysis date, dormancy and activity windows, after-hours definition, comparison-population minimums, heartbeat period, change-rate comparison requirements, reconciliation aging, settlement grace, amount tolerance, approval threshold, and review-priority weights.

An adopting institution must approve its own thresholds, calendars, conflict matrix, priorities, and escalation service levels. Boundary testing should cover values immediately below, at, and above each applicable threshold. Reference SQL must also be adapted and tested for the target database and approved configuration.

### What transfers and what must be tailored

CCAF separates reusable assurance mechanics from institution-specific decisions. This allows another authorized institution or practitioner to adapt the methodology without treating the demonstration as a plug-and-play production system.

| Reusable framework components | Institution-specific tailoring and validation |
|---|---|
| Modular control-test structure; transparent rule and comparison logic; Completed and Not Evaluable outcomes; eligible-population and exception records; evidence-bundle and run-metadata pattern; exception-to-conclusion workflow. | Source systems and field mappings; extraction queries and reconciliations; policies, thresholds, calendars, peer groups, and conflict matrices; roles and approvals; privacy, retention, escalation, integration, and remediation requirements. |

Transfer therefore means that the documented method and evidence structure can be adapted after local mapping, authorization, calibration, and validation. It does not mean that bundled settings or synthetic results are suitable for production use without that work.

## 7. From exception to conclusion

An exception is the beginning of a judgment, not the end of one. CCAF uses the following conclusion sequence:

1. An **automated exception** means the coded condition was met.
2. An **investigated condition** means a reviewer examined supporting records and context.
3. A **confirmed deviation** means the applicable control requirement was not performed as designed.
4. A **deficiency or finding** results only after authorized personnel evaluate the confirmed deviation under the institution's methodology.

CCAF produces the first item and structures evidence for the later steps. No statistical or rule-based exception establishes misconduct, control failure, or deficiency without investigation.

This sequence sits within a broader control-assurance lifecycle:

| Stage | Practitioner question | Evidence normally required |
|---|---|---|
| Scope and design | What risk and control requirement are being evaluated? | Risk, objective, owner, frequency, systems, period, and population |
| Implementation | Is the control configured and operating in the intended environment? | Configuration, roles, walkthrough, rule version, and environment evidence |
| Source reliability | Are the supplied records authorized, complete and accurate, and correctly filtered? | Queries or reports used to generate the extract, parameters, expected counts or totals, period coverage, and owner review |
| Execution | What procedure was performed, over what population, and with what result? | Test logic, effective configuration, evaluation status, population, and exceptions |
| Follow-up | What did investigation establish? | Reviewer, source evidence, disposition, remediation, escalation, and closure |
| Rollforward | Have changes to code, configuration, source logic, or process ownership affected consistent operation since testing? | Change history, version comparison, impact assessment, and period-end work |

CCAF supports execution and evidence organization. Production conclusions require the other stages as well.

## 8. Limitations

- A result covers only the supplied in-scope records and the stated test.
- Production use requires authorization, field mapping, privacy review, source reconciliation, threshold approval, human review, and controlled remediation.
- PA-05 contains illustrative segregation-of-duties pairs that must be replaced or expanded using the institution's conflict matrix.
- Weekday aging does not account for federal, market, or institution-specific holidays.
- Reconciliation tests assume the supplied single-currency demonstration structure; production use must address currencies, fees, reversals, partial settlements, and product rules.
- Comparison tests require representative populations and institution-approved grouping logic.
- Reference SQL must be adapted and tested for the target database and approved configuration.
- Synthetic results do not establish adoption, supervisory acceptance, external validation, production performance, or real-world impact.
