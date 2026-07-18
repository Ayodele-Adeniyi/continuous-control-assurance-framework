# Independent Technical Review Guide

This guide supports an identifiable review of a specific CCAF release or commit. The primary purpose is to assess whether the methodology is coherent, technically sound, appropriately bounded, and adaptable to authorized institutional environments. The normal review is document based; GitHub access, local installation, and command-line execution are optional. The questions below are prompts to structure a review, not a form that must be completed, and a reviewer may address any subset relevant to the materials examined and the reviewer's expertise.

## Choose the review depth

### Methodology-focused review (recommended)

Use the attached methodology summary and control-test catalog for a concise design review. This route normally takes about 20 minutes and does not require software installation or code execution. The recommended sequence is:

1. identifying the review snapshot and any prior relationship, conflict, or compensation involving the author;
2. reading the concise methodology summary to understand the objective, workflow, outputs, limitations, and evidence boundaries;
3. reviewing the control-test catalog, including the risks, intended control states, automated procedures, and required follow-up evidence for selected tests; and
4. recording an overall professional opinion and any observations in the reviewer's own words.

A document review is a professional assessment of the framework's design. It is not a claim that the reviewer reproduced the software or independently verified its documented output. The response form separates those procedures so the reviewer can describe only what was personally examined.

The methodology-focused review may use the [Markdown response template](REVIEW_RESPONSE_TEMPLATE.md) or the [Word response form](docs/CCAF_Independent_Review_Response_Template.docx). The Word form is generated from the Markdown source. It uses three concise professional-opinion selections and one short reviewer-authored overall assessment, so a reviewer can provide a useful signed response without preparing a long report.

### Source-code and local-reproduction review (optional)

A reviewer who wishes to inspect the implementation or reproduce the documented result may use the public GitHub repository. This is optional and is not required for the methodology-focused design review.

One-time setup:

```bash
python -m pip install -r requirements.txt
```

Demonstration command:

```bash
python run_all.py --regenerate --seed 42 --no-charts
```

Seed `42` reproduces the official release benchmark. A reviewer may substitute another integer to test whether the generator and evidence process remain reproducible under a different synthetic population. Any such result must be identified as exploratory and reported with its seed.

### Detailed source-code review (optional)

Use this route when the reviewer wants to examine selected controls, boundaries, code, and implementation assumptions in greater depth. Local reproduction and the automated test suite remain optional procedures chosen by the reviewer. To run the test suite:

```bash
python -m unittest discover -s tests -v
```

The reviewer may then inspect selected tests and use any of the optional detailed prompts below. The reviewer determines the appropriate depth and procedures.

## Release and reproduction facts

For Version 1.3.1, the repository documents the following mechanical facts. Reviewers should distinguish these documented release claims from results they personally observe and correct any discrepancy:

- code release tag: `v1.3.1`;
- stable reviewer snapshot: `review-v1.3.1`;
- license: Apache-2.0;
- 20 control tests, each with an explicit Completed or Not Evaluable status;
- synthetic demonstration data only;
- an official seed-42 benchmark result of 165 of 165 deliberately planted conditions detected, with 3 additional peer-comparison observations reported separately and 168 total exceptions; and
- input hashes, configuration details, rule versions, and run metadata retained as reproducibility evidence.

These are documented release facts, not requested conclusions. The author may pre-fill them in a response template. A reviewer who reproduces the demonstration should separately record the seed and result personally observed. A documents-only reviewer should not check a reproduction procedure. The reviewer's professional opinions, limitations, and observations must be written by the reviewer.

## Focused professional-opinion response

The concise form records the reviewer's judgment in three areas: technical soundness, whether the claims are appropriately bounded, and potential adaptation by other institutions or practitioners. It then asks for a brief overall assessment in the reviewer's own words. Optional comment lines allow the reviewer to explain reservations or identify improvements without turning the response into a lengthy questionnaire. A critical observation is useful evidence of an authentic review, and the framework author may respond through a documented correction or later release.

## Optional detailed prompts

Use the control-test catalog, methodology summary, and optional repository documentation as needed:

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
