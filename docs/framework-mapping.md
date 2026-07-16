# Framework Traceability

This crosswalk identifies framework outcomes or examination topics to which a CCAF result may be relevant. It is a documentation aid, not a determination of compliance, control effectiveness, or examination sufficiency. NIST, FFIEC, PCI SSC, and other referenced bodies have not reviewed or endorsed CCAF. The FFIEC CAT sunset statement expressly notes that the FFIEC does not endorse a particular replacement tool.

Mappings are stated at category, topic, or requirement-area level. An adopting institution must confirm the current framework text, scope, and applicability.

## Module 1 - Privileged Access

| Test | Control objective | Potentially relevant NIST CSF 2.0 outcome | FFIEC topic | SOX ITGC domain | PCI DSS area |
|---|---|---|---|---|---|
| PA-01 | Revoke access after separation | PR.AA | Information Security - access administration | Access to programs and data | Requirements 7, 8 |
| PA-02 | Authorize access before provisioning | PR.AA; GV.RR | Information Security - authorization | Access to programs and data | Requirement 7 |
| PA-03 | Prevent self-authorization | PR.AA; GV.RR | Information Security - segregation of duties | Access to programs and data | Requirement 7 |
| PA-04 | Review unused privileged access | PR.AA | Information Security - access review | Access to programs and data | Requirement 8 |
| PA-05 | Prevent toxic entitlement combinations | PR.AA; GV.RR | Information Security - segregation of duties | Access to programs and data | Requirement 7 |
| PA-06 | Review unusual privileged activity | DE.CM; DE.AE | Information Security - logging and monitoring | Access to programs and data | Requirement 10 |
| PA-07 | Revoke temporary privileged access at expiry | PR.AA; GV.RR | Information Security - access administration | Access to programs and data | Requirements 7, 8 |

## Module 2 - Change Management and Logging

| Test | Control objective | Potentially relevant NIST CSF 2.0 outcome | FFIEC topic | SOX ITGC domain | PCI DSS area |
|---|---|---|---|---|---|
| CM-01 | Authorize changes before implementation | PR.PS; GV.PO | Development, Acquisition, and Maintenance | Program changes | Requirement 6 |
| CM-02 | Segregate change duties | PR.PS; GV.RR | Development, Acquisition, and Maintenance | Program changes | Requirement 6 |
| CM-03 | Review emergency changes retrospectively | PR.PS | Development, Acquisition, and Maintenance | Program changes | Requirement 6 |
| CM-04 | Trace deployments to change records | DE.CM; PR.PS | Architecture, Infrastructure, and Operations | Program changes | Requirements 6, 10 |
| CM-05 | Monitor logging continuity | DE.CM | Information Security - logging | Computer operations | Requirement 10 |
| CM-06 | Review abnormal change patterns | DE.AE | Development, Acquisition, and Maintenance | Program changes | Requirement 6 |
| CM-07 | Confirm testing before production implementation | PR.PS; GV.PO | Development, Acquisition, and Maintenance | Program changes | Requirement 6 |

## Module 3 - Reconciliation and Payment Anomaly

The NIST and PCI entries below are **supporting relationships**, not direct financial-reconciliation requirements. FFIEC payment-system topics and the institution's own payment-control requirements should govern the primary mapping.

| Test | Control objective | Supporting NIST CSF 2.0 relationship | FFIEC topic | SOX ITGC relationship | PCI DSS relationship |
|---|---|---|---|---|---|
| TR-01 | Identify unmatched settlement items | DE.CM | Retail Payment Systems - reconciliation | Computer operations | Audit evidence may be relevant to Requirement 10 |
| TR-02 | Identify settlement amount differences | DE.AE | Retail Payment Systems - reconciliation | Computer operations | No direct mapping claimed |
| TR-03 | Identify duplicate transaction identifiers | DE.AE | Retail Payment Systems - payment integrity | Computer operations | No direct mapping claimed |
| TR-04 | Escalate aged unreconciled items | DE.CM | Retail Payment Systems - reconciliation | Computer operations | No direct mapping claimed |
| TR-05 | Screen unusual account activity | DE.CM; DE.AE | Retail Payment Systems - monitoring | No direct mapping claimed | Logging evidence may be relevant to Requirement 10 |
| TR-06 | Review repeated activity below an authorization limit | DE.AE | Retail Payment Systems - authorization | No direct mapping claimed | No direct mapping claimed |

## Permitted interpretation

CCAF results may help an institution organize evidence, identify exceptions, and trace analytics to its own control inventory. They do not by themselves demonstrate that a NIST outcome, FFIEC examination objective, SOX assertion, or PCI DSS requirement is satisfied. See `docs/references.md` for source materials.
