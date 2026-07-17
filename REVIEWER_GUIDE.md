# Independent Technical Review Guide

This guide supports an identifiable review of a specific CCAF release. A review should state the version and commit examined, the reviewer's relevant experience, the procedures performed, findings or limitations identified, and any conflict of interest.

## 1. Confirm the reviewed release

Record the release version and tag, commit hash, review date, reviewer name and role, relevant experience, and any prior relationship with the author. Review the tagged release rather than an unpublished working copy.

## 2. Reproduce the demonstration

```bash
python -m pip install -r requirements.txt
python run_all.py --regenerate --no-charts
python -m unittest discover -s tests -v
```

Confirm that:

- the test suite passes;
- `output/run_metadata.json` records the expected version and configuration hash;
- all 20 test evaluations have an explicit status;
- the synthetic release reports 165 of 165 planted conditions detected; and
- input hashes and generated summaries are reproducible.

## 3. Review the methodology and evidence model

Use `docs/control-test-catalog.md`, `docs/methodology.md`, and `docs/architecture.md` to assess:

1. whether each risk and control objective is understandable;
2. whether the required records, eligible population, period, and procedure are defined;
3. whether Completed and Not Evaluable results are distinguished correctly;
4. whether data-quality checks stop unreliable runs before control-test execution;
5. whether source completeness and accuracy remain subject to independent evidence;
6. whether thresholds, calendars, comparison populations, priorities, and other assumptions are explicit; and
7. whether an automated exception is appropriately distinguished from a deviation or deficiency.

## 4. Inspect selected tests in depth

Review at least one test from each module and at least one comparison-based test. For each selected test:

- trace the catalog description to the Python implementation;
- confirm the eligible-population calculation;
- inspect one planted positive condition and one non-exception record;
- test an applicable boundary or minimum-condition case;
- confirm the exception includes the source entity, rule version, and review priority; and
- note any false-negative exposure or institution-specific assumption.

Suggested coverage is PA-04 or PA-06, CM-01 or CM-06, and TR-02, TR-04, or TR-05.

## 5. Assess adaptation boundaries

Confirm that the repository does not claim source-system completeness from file hashes, production accuracy from synthetic results, compliance or agency endorsement, operating effectiveness from exceptions alone, or institutional adoption without external evidence.

Assess whether an authorized institution could adapt the schemas, source-metadata record, configuration, conflict matrix, calendars, and follow-up workflow without using proprietary source materials.

## 6. Suggested review statement structure

A useful statement identifies:

1. the exact release reviewed;
2. the reviewer's qualifications and independence;
3. the procedures performed;
4. the aspects found technically credible;
5. material limitations or recommended changes; and
6. whether the framework could be adapted across institutions after local authorization, mapping, calibration, and validation.

Useful evidence includes a public GitHub issue, pull-request review, signed memorandum, or professional email tied to the exact release. General praise without technical procedures carries less evidentiary value. Independent review is not institutional adoption, regulatory approval, certification, or assurance over production performance.
