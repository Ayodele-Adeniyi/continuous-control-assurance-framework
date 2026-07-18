# Independent Technical Review Guide

This guide supports an identifiable review of a specific CCAF release or commit. The primary purpose is to assess whether the methodology is coherent, technically sound, appropriately bounded, and adaptable to authorized institutional environments. The interactive website contains the normal review path; GitHub access, local installation, and command-line execution are not required. The questions below are prompts to structure a review, not a form that must be completed, and a reviewer may address any subset relevant to the materials examined and the reviewer's expertise.

## Choose the review depth

### Methodology-focused review (recommended)

Use the [interactive reviewer website](https://continuous-control-assurance.streamlit.app/) for a concise independent professional assessment without installing software. The recommended sequence is:

1. identifying the release or commit reviewed and any prior relationship, conflict, or compensation involving the author;
2. reading the website's Overview to understand the objective, workflow, intended users, outputs, and evidence boundaries;
3. using Controls to inspect the risk, intended control state, automated procedure, and expected evidence for selected tests;
4. using Run Demo to execute the fixed synthetic demonstration with one browser click and record the result personally observed;
5. using Evidence to inspect selected source, configuration, population, exception, and reproducibility artifacts; and
6. providing an overall professional opinion and any observations in the reviewer's own words under Review.

The website requires no local setup and includes the methodology summary, reviewer guide, and response template. It supports inspection and browser-based execution, but does not replace the reviewer's professional judgment. A reviewer should describe only the materials and procedures personally examined.

The methodology-focused review may use the [Markdown response template](REVIEW_RESPONSE_TEMPLATE.md) or the [Word response form](docs/CCAF_Independent_Review_Response_Template.docx). The Word form is generated from the Markdown source so the prompts remain synchronized. Brief responses are acceptable. The reviewer does not need to answer every prompt or prepare a long report.

### Source-code and local-reproduction review (optional)

A reviewer who wishes to inspect the source code or reproduce the documented result outside the website may use the GitHub repository. This is optional and is not required for the methodology-focused review.

One-time setup:

One-time setup:

```bash
python -m pip install -r requirements.txt
```

Demonstration command:

```bash
python run_all.py --regenerate --no-charts
```

### Detailed source-code review (optional)

Use this route when the reviewer wants to examine selected controls, boundaries, code, and implementation assumptions in greater depth. Local reproduction and the automated test suite remain optional procedures chosen by the reviewer. To run the test suite:

```bash
python -m unittest discover -s tests -v
```

The reviewer may then inspect selected tests and use any of the optional detailed prompts below. The reviewer determines the appropriate depth and procedures.

## Release and reproduction facts

For Version 1.3.1, the repository documents the following mechanical facts. Reviewers should distinguish these documented release claims from results they personally observe and correct any discrepancy:

- release tag: `v1.3.1`;
- license: Apache-2.0;
- 20 control tests, each with an explicit Completed or Not Evaluable status;
- synthetic demonstration data only;
- a documented release result of 165 of 165 deliberately planted conditions detected; and
- input hashes, configuration details, rule versions, and run metadata retained as reproducibility evidence.

These are documented release facts, not requested conclusions. The author may pre-fill them in a response template. A reviewer who runs the website demonstration should separately record the browser result personally observed. A reviewer who also reproduces the demonstration locally should identify that additional procedure. The reviewer's professional opinions, limitations, and observations must be written by the reviewer.

## Four focused opinion prompts

Reviewers may address any subset in their own words:

1. Is the methodology technically sound and consistent with professional control-testing practice for a synthetic reference prototype?
2. Are its claims and limitations appropriately bounded to what the demonstration establishes?
3. In your professional judgment, could this methodology be adapted by other institutions or practitioners to their own authorized data and control environments?
4. What observations, limitations, or improvements, if any, would you note?

A critical observation is useful evidence of an authentic review. The framework author may respond through a documented correction or later release.

## Optional detailed prompts

Use `docs/control-test-catalog.md`, `docs/methodology.md`, and `docs/architecture.md` as needed:

1. Are the risks and expected control conditions understandable?
2. Are the required records, eligible populations, periods, and procedures adequately defined?
3. Are Completed and Not Evaluable outcomes distinguished appropriately?
4. Do data-quality checks stop unreliable runs before control-test execution?
5. Does the documentation appropriately reserve source completeness and accuracy for independent evidence?
6. Are thresholds, calendars, comparison populations, priorities, and tailoring assumptions explicit?
7. Are automated exceptions appropriately distinguished from deviations, deficiencies, and risk conclusions?
8. Could an authorized institution adapt the schemas, configuration, source-metadata record, and follow-up workflow after local mapping, calibration, and validation?

For a deeper control trace, review at least one test from each module and one comparison-based test. Suggested coverage is PA-04 or PA-06, CM-01 or CM-06, and TR-02, TR-04, or TR-05. A reviewer may trace the catalog description to the Python implementation, inspect the eligible population, examine one planted condition and one non-exception record, and note institution-specific assumptions.

## Evidence boundaries

CCAF does not claim source-system completeness from file hashes, production accuracy from synthetic results, compliance or agency endorsement, operating effectiveness from exceptions alone, or institutional adoption without external evidence. Independent review is not institutional adoption, regulatory approval, certification, or assurance over production performance.

## Ways to provide feedback

Feedback may be provided through the concise response template, a signed memorandum, professional email, public GitHub issue, pull-request review, or another authentic record tied to the release or commit examined. General praise without identifying the materials and procedures reviewed is less useful than a brief statement explaining what the reviewer examined and the professional judgment reached. Reviewers should be informed that their response may be cited publicly and in professional or immigration-related submissions as evidence of independent review.
