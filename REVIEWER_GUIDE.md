# Independent Technical Review Guide

This guide supports an identifiable review of a specific CCAF release. The questions below are prompts to structure a review, not a form that must be completed. A reviewer may address any subset relevant to the procedures performed and the reviewer's expertise.

## Choose the review depth

### Focused review

Use this route for a concise independent assessment. Excluding the one-time dependency installation, the focused route normally takes about 25 to 30 minutes. The documented demonstration is reproduced with one command. A focused review normally consists of:

1. identifying the release or commit reviewed and any prior relationship, conflict, or compensation involving the author;
2. reproducing the synthetic demonstration;
3. reading the methodology summary and stated limitations; and
4. providing an overall professional opinion and any observations in the reviewer's own words.

One-time setup:

```bash
python -m pip install -r requirements.txt
```

Reproduction command:

```bash
python run_all.py --regenerate --no-charts
```

The focused review may use the [Markdown response template](REVIEW_RESPONSE_TEMPLATE.md) or the [Word response form](docs/CCAF_Independent_Review_Response_Template.docx). The Word form is generated from the Markdown source so the prompts remain synchronized. Brief responses are acceptable. The reviewer does not need to answer every prompt or prepare a long report.

### Detailed review

Use this route when the reviewer wants to examine selected controls, boundaries, and implementation assumptions in greater depth. In addition to the focused review, run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

Then inspect selected tests and use any of the optional detailed prompts below. The reviewer determines the appropriate depth and procedures.

## Release and reproduction facts

For Version 1.3.1, the repository documents the following mechanical facts. Reviewers should distinguish these documented release claims from results they personally observe and correct any discrepancy:

- release tag: `v1.3.1`;
- license: Apache-2.0;
- 20 control tests, each with an explicit Completed or Not Evaluable status;
- synthetic demonstration data only;
- a documented release result of 165 of 165 deliberately planted conditions detected; and
- input hashes, configuration details, rule versions, and run metadata retained as reproducibility evidence.

These are verifiable release facts, not requested conclusions. The author may pre-fill them in a response template. A reviewer who reproduces the demonstration should separately record the result personally observed. The reviewer's professional opinions, limitations, and observations must be written by the reviewer.

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

Feedback may be provided through the concise response template, a signed memorandum, professional email, public GitHub issue, pull-request review, or another authentic record tied to the release examined. General praise without identifying the release or procedures performed is less useful than a brief statement showing what the reviewer actually examined. Reviewers should be informed that their response may be cited publicly and in professional or immigration-related submissions as evidence of independent review.
