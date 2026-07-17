# CCAF Control-Test Catalog

This catalog is the practitioner work program for Version 1.3.1. It explains what each test is intended to address, the records and population it evaluates, the procedure it performs, and the review required after an exception is reported. The tests identify conditions for investigation. They do not, by themselves, establish a control deviation, deficiency, misconduct, compliance failure, or financial loss.

## How to read an evaluation

Each test records one of two statuses:

- **Completed:** the required records and analytical preconditions were present, so the reported exception count and rate may be interpreted for the supplied population.
- **Not Evaluable:** a stated precondition was not met. No exception rate is calculated, and the result must not be described as a clean test.

Review-priority labels are demonstration settings for ordering follow-up. They are not institutional risk ratings. Before operational use, the adopting institution must approve the objective, population, period, source reliability, threshold, priority, reviewer, and escalation route.

## Module 1: Privileged Access

| ID | Risk and objective | Records and eligible population | Procedure and exception | Default priority | Required review and limitations |
|---|---|---|---|---|---|
| PA-01 | Separated personnel retain elevated access. Identify active privileged grants held by terminated users. | User roster and active privileged grants. Population: active privileged grants. | Join grants to the user roster and report a grant when the user status is terminated. | Critical | Confirm termination date, grant status, approved exceptions, and revocation evidence. Source rosters and grant inventories must be complete. |
| PA-02 | Privileged access is provisioned without recorded authorization. | Active privileged grants. Population: active privileged grants. | Report a grant when the approver field is blank. | High | Inspect the authoritative request and approval record. A missing field may reflect mapping failure rather than missing authorization. |
| PA-03 | A user authorizes the user's own access. | Active access grants. Population: active grants. | Report a grant when grantee and approver identifiers match. | High | Confirm identifier mapping, delegated approvals, service accounts, and applicable segregation policy. |
| PA-04 | Unused privileged access remains available. | Active privileged users and successful authentication events. Population: active privileged users. | Report a user whose latest successful authentication is at least the configured dormancy period ago, or for whom no successful event exists in a supplied period that covers the dormancy threshold. | Medium | Confirm log coverage, alternate authentication paths, approved standby accounts, and current business need. The test is Not Evaluable when the extract does not cover the dormancy period. |
| PA-05 | One user holds an incompatible combination of entitlements. | Active grants grouped by user. Population: users with active grants. | Report a user holding both entitlements in a configured conflict pair. | Critical | Validate the institution's role and conflict matrix, compensating controls, and approved exceptions. Version 1.3.1 contains three illustrative conflict pairs that must be replaced or expanded locally. |
| PA-06 | Unusual after-hours privileged activity is not investigated. | Successful authentication events for active privileged users during the configured activity window. Population: active privileged users. | Count after-hours events by user, compare counts with the supplied comparison population using a median-based outlier score, and report values meeting the configured threshold. | Medium | Review timezone, role, maintenance windows, event coverage, and expected activity. The test is Not Evaluable below the minimum comparison population or when counts have no usable variation. An outlier is not evidence of misconduct. |
| PA-07 | Temporary privileged access remains active after its approved expiry. | Active temporary privileged grants. Population: active temporary privileged grants. | Report a grant whose expiry precedes the as-of time after the configured grace period. | Critical | Confirm the approved expiry, emergency-access procedure, actual revocation state, and any authorized extension. |

## Module 2: Change Management and Logging

| ID | Risk and objective | Records and eligible population | Procedure and exception | Default priority | Required review and limitations |
|---|---|---|---|---|---|
| CM-01 | A production change is implemented without recorded approval. | Implemented change records. Population: supplied change records. | Report a change when the approver or approval timestamp is missing. | High | Inspect the authoritative workflow, emergency procedure, approval evidence, and field mapping. |
| CM-02 | Approval and implementation duties are not segregated. | Implemented change records. Population: supplied change records. | Report a change when approver and implementer identifiers match. | High | Confirm role mappings, automated deployments, delegated approvals, and approved exceptions. |
| CM-03 | An emergency change is not reviewed after implementation. | Emergency change records. Population: emergency changes. | Report an emergency change when the post-implementation-review indicator is false. | Medium | Inspect review evidence, completion timing, closure requirements, and any outstanding remediation. |
| CM-04 | A deployment cannot be traced to an approved change record. | Deployment events and change records. Population: deployment events. | Report a deployment with a blank change reference or a reference absent from the supplied change population. | Critical | Confirm interface completeness, bundled deployments, automated release identifiers, and emergency deployment procedures. |
| CM-05 | A required log source stops reporting. | Log-source heartbeat records. Population: configured log sources. | Report a source whose most recent event is at least the configured heartbeat threshold before the as-of time. | High | Confirm source criticality, expected cadence, maintenance windows, clock synchronization, and collection-platform health. |
| CM-06 | The recent emergency-change rate materially exceeds the historical baseline. | Recent and baseline change records. Population: one portfolio comparison. | Compare the recent emergency-change rate with the earlier supplied baseline and report when the configured ratio is met. | Medium | Investigate release events, outages, classification changes, and baseline comparability. The test is Not Evaluable when minimum recent or baseline counts are not met or the baseline contains no emergency changes. |
| CM-07 | A production change lacks recorded preproduction testing. | Implemented change records. Population: supplied change records. | Report a change when testing is not marked complete or the test approver is blank. | High | Inspect test evidence, test approval, emergency exceptions, production parity, and deployment authorization. |

## Module 3: Reconciliation and Payments

| ID | Risk and objective | Records and eligible population | Procedure and exception | Default priority | Required review and limitations |
|---|---|---|---|---|---|
| TR-01 | A due ledger item has no corresponding processor settlement. | Ledger and processor-settlement records. Population: ledger items at or beyond the configured settlement grace period. | Left-join on transaction identifier and report due ledger items without a processor match. | High | Confirm settlement timing, rejected or reversed transactions, alternate identifiers, cut-off, and extract completeness. The bundled grace period is a demonstration value. |
| TR-02 | Ledger and processor amounts differ beyond the approved tolerance. | Matched ledger and processor records. Population: matched transaction identifiers. | Calculate the absolute amount difference and report values above the configured tolerance. | High | Confirm currency, rounding, fees, partial settlements, reversals, and the approved reconciliation rule. Version 1.3.1 assumes a single-currency demonstration. |
| TR-03 | A transaction identifier appears more than once in the ledger. | Ledger records. Population: unique supplied transaction identifiers. | Report identifiers associated with more than one ledger row. | Critical | Determine whether the identifier is required to be unique and whether split postings, reversals, or multi-leg transactions are legitimate. |
| TR-04 | An unreconciled item remains open beyond the approved aging threshold. | Unreconciled ledger records. Population: unreconciled ledger items. | Count weekdays from booking to the as-of date and report items exceeding the configured threshold. | Medium | Confirm settlement calendars, holidays, cut-off, status accuracy, ownership, and remediation. The bundled code counts weekdays only. |
| TR-05 | An account's recent transaction volume is unusually high relative to the supplied comparison population. | Recent ledger activity grouped by account. Population: active accounts in the configured window. | Compare account transaction counts using a median-based outlier score and report values meeting the configured threshold. | Medium | Review account type, seasonality, batch activity, product differences, and peer-group design. The test is Not Evaluable below the minimum comparison population or when counts have no usable variation. |
| TR-06 | Threshold hovering below approval limit. Repeated transactions cluster immediately below an approval threshold. | Ledger activity grouped by account. Population: accounts represented in the supplied ledger. | Count transactions in the configured band below the approval limit and report accounts meeting the minimum count. | High | Confirm the applicable authorization matrix, aggregation period, product context, legitimate recurring activity, and potential transaction splitting. |

## Evidence and conclusion protocol

For every completed test, retain the configuration, source-assurance record, data-quality results, evaluation status, eligible population, exception records, rule version, input hashes, reviewer disposition, and supporting evidence. Use the following conclusion sequence:

1. **Automated exception:** the coded condition was met.
2. **Investigated condition:** a reviewer examined source evidence and context.
3. **Confirmed deviation:** the reviewer established that the relevant control requirement was not performed as designed.
4. **Deficiency or finding:** authorized assurance, risk, compliance, or control owners evaluated the deviation's significance under the institution's methodology.

CCAF produces the first item and structures evidence for the remaining steps. It does not make the later determinations automatically.
