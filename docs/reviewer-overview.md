# CCAF Reviewer Overview

**Version 1.3.1 | Synthetic Reference Prototype | Stable snapshot: `review-v1.3.1`**

## What CCAF is

The Continuous Control Assurance Framework (CCAF) is a documented methodology and open-source reference implementation for applying repeatable analytics to authorized data extracts. It helps audit, risk, and cybersecurity teams expand beyond periodic sampling by testing every eligible record in the supplied in-scope extract and organizing reported conditions for professional follow-up.

CCAF does not establish that a source extract is complete, determine control effectiveness, or make remediation decisions. It applies transparent procedures consistently and preserves the evidence needed to understand and reproduce the run.

## How it works

Authorized extracts and source metadata -> data-quality and source-assurance checks -> 20 versioned control procedures -> evaluation status, eligible population, and exceptions -> reproducibility evidence -> professional investigation and institutional conclusion.

## What it tests

| Module | Tests | Focus | Example condition reported for review |
|---|---:|---|---|
| Privileged Access | 7 | Access status, approval, incompatible rights, dormancy, peer activity, and expiry | A terminated user retains active privileged access |
| Change Management and Logging | 7 | Change approval, separation of duties, emergency review, deployment traceability, logging, and testing | A production deployment lacks a valid change record |
| Reconciliation and Payments | 6 | Settlement matching, amount tolerance, duplicate identifiers, aging, peer activity, and threshold patterns | A due ledger item lacks a processor-settlement record |

## What the fixed demonstration establishes

The official seed-42 synthetic benchmark contains a known answer key. Version 1.3.1 reported all 165 deliberately planted conditions: 39 in Privileged Access, 49 in Change Management and Logging, and 77 in Reconciliation and Payments. It also reported 3 additional peer-comparison observations, producing 168 total exceptions.

This is regression evidence that the released code detects the conditions deliberately built into the fixed synthetic scenario. It is not a production detection rate, external validation, or evidence of institutional adoption.

## Interpretation boundaries

- Synthetic demonstration data only; no employer, client, or production information is included.
- "Every eligible record" refers only to the supplied in-scope extract, not an institution's unverified full population.
- A reported exception is a condition for investigation, not a confirmed control deviation or deficiency.
- The 20 tests are a bounded reference set that complements, rather than replaces, enterprise security, GRC, audit, or monitoring platforms.
- No institutional adoption, regulatory approval, certification, external validation, or production performance is claimed.

## For the reviewer

A documents-based design review of the methodology and control-test catalog is sufficient. Repository inspection and local reproduction are optional. The response should identify the materials and procedures personally examined and reflect the reviewer's independent professional judgment.

# CCAF Control-Test Quick Reference

**20 detective procedures | Three modules | Version 1.3.1**

| ID | Procedure focus | Example condition reported for review |
|---|---|---|
| PA-01 | Active privileged access after termination | Terminated user retains an active privileged grant |
| PA-02 | Recorded approval before privileged access activation | Active grant has no recorded approver |
| PA-03 | Separation of grantee and approver | User approved the user's own access |
| PA-04 | Dormant privileged access | No successful authentication within the approved dormancy period |
| PA-05 | Incompatible entitlements | User holds an institution-defined conflicting entitlement pair |
| PA-06 | Unusual after-hours privileged activity | Activity exceeds the approved peer-comparison threshold |
| PA-07 | Expired temporary privileged access | Temporary grant remains active after approved expiry and grace period |
| CM-01 | Recorded approval for implemented production changes | Implemented change has no recorded approver or approval time |
| CM-02 | Separation of change approval and implementation | Same identifier approved and implemented a change |
| CM-03 | Post-implementation review of emergency changes | Emergency change lacks recorded post-implementation review |
| CM-04 | Deployment linked to a valid change record | Production deployment lacks a valid change reference |
| CM-05 | Timely reporting by required log sources | Required source exceeds the approved heartbeat interval |
| CM-06 | Emergency-change rate against historical baseline | Recent rate meets the configured increase threshold |
| CM-07 | Recorded preproduction testing and approval | Implemented change lacks testing or test approval evidence |
| TR-01 | Ledger-to-processor settlement matching | Due ledger item lacks a processor-settlement record |
| TR-02 | Amount consistency within approved tolerance | Matched amounts differ beyond the approved tolerance |
| TR-03 | Transaction-identifier uniqueness | Identifier appears in more than one ledger row |
| TR-04 | Aging of unreconciled items | Open item exceeds the approved aging period |
| TR-05 | Unusual transaction velocity | Account activity exceeds the approved peer-comparison threshold |
| TR-06 | Repeated transactions below an approval limit | Account meets the configured threshold-hovering pattern |

## How to interpret the results

- **Completed:** required records and analytical conditions were present; the result applies only to the reported eligible population.
- **Not Evaluable:** a required condition was absent; no clean result or exception rate is implied.
- **Institutional tailoring:** source mappings, extraction evidence, thresholds, calendars, policies, peer groups, conflict matrices, roles, and escalation requirements must be authorized and validated locally.
- **Evidence retained:** approved configuration, source queries or reports, source-assurance record, data-quality results, evaluation status, eligible population, exceptions, rule version, input hashes, reviewer disposition, and supporting records.

An automated exception begins professional investigation. It does not by itself establish a control deviation, deficiency, misconduct, compliance failure, or financial loss.
