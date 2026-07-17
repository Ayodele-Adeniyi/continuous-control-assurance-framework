# Implementation Checklist

## Phase 0 - Authorization and control design

- [ ] Obtain written authorization from data owners and security/privacy stakeholders.
- [ ] Define the risk, control objective, owner, frequency, systems, period, and eligible population.
- [ ] Define the nature, timing, and extent of the procedure and the evidence required to support its conclusion.
- [ ] Distinguish manual, configurable, and coded components of the control.
- [ ] Map source fields to CCAF schemas without placing credentials in code.
- [ ] Approve institution-specific thresholds, calendars, review-priority definitions, and escalation paths.
- [ ] Record changes in a controlled configuration and calibration log.

## Phase 1 - Source reliability

- [ ] Record the source system, environment, extract date, owner, query or report reference, and filter parameters.
- [ ] Complete and approve the source-metadata record required for institutional extracts.
- [ ] Confirm timezone, period start and end, and whether late-arriving records are possible.
- [ ] Reconcile actual row counts and financial control totals to independent expected values.
- [ ] Validate key uniqueness, field types, relationships, and required timestamps.
- [ ] Preserve extraction logic and a cryptographic hash of the reviewed file.
- [ ] Resolve blocking data-quality findings before executing control analytics.

## Phase 2 - Design and implementation evidence

- [ ] Confirm that the analytics rule addresses the defined control objective and relevant population.
- [ ] Verify the effective configuration, roles, thresholds, tolerances, and approval limits.
- [ ] Test applicable boundaries immediately below, at, and above configured limits.
- [ ] If testing outside production, document production parity for relevant code and configuration.
- [ ] Confirm that changes to rules or source systems are authorized, tested, and traceable.

## Phase 3 - Historical pilot

- [ ] Begin with one module whose source data is sufficiently complete.
- [ ] Execute against an authorized historical period.
- [ ] Have control owners adjudicate every exception.
- [ ] Distinguish automated exceptions, investigated conditions, confirmed deviations, and deficiencies or findings.
- [ ] Measure seeded-condition detection where known test conditions exist, actionable exception rate, reviewer effort, and detection latency.
- [ ] Document false-positive and false-negative causes before changing thresholds.
- [ ] Confirm period coverage and perform rollforward work when testing precedes period end.

## Phase 4 - Operationalization

- [ ] Replace weekday aging with the approved holiday and settlement calendar.
- [ ] Schedule runs according to source cadence and control risk.
- [ ] Route exceptions into the institution's ticketing or GRC process.
- [ ] Retain reviewer, disposition, supporting evidence, remediation reference, and closure date.
- [ ] Apply approved remediation service levels and evidence retention.
- [ ] Restrict dashboards and exception files according to data classification.

## Phase 5 - Governance and expansion

- [ ] Obtain model, audit, compliance, or risk approval appropriate to the institution.
- [ ] Monitor drift, recurrence, adjudication outcomes, and control coverage.
- [ ] Revalidate after material changes to systems, interfaces, mappings, roles, or thresholds.
- [ ] Train a second operator and document recovery and handoff procedures.
- [ ] Contribute only nonconfidential improvements to any public release.

## Minimum extracts

| Module | Required extracts | Typical authorized sources |
|---|---|---|
| Privileged Access | user roster, entitlement grants, temporary-access expiry, authentication events | HR/IAM, directory, privileged-access platform, SIEM |
| Change and Logging | change records, test evidence, deployment events, log-source heartbeats | ITSM, CI/CD, test repository, logging platform |
| Reconciliation and Payments | ledger, processor settlement, transaction attributes | core banking, processor, payment network |
