# Independent Technical Review Guide

This guide supports an identifiable review of a specific CCAF release. A review should state the version and commit examined, the reviewer's relevant experience, the procedures performed, and any limitations or conflicts of interest.

## Reproduce the demonstration

The [architecture guide](architecture.md) documents the module contract and input schemas referenced by questions 5 and 8.

```bash
python -m pip install -r requirements.txt
python run_all.py --regenerate --no-charts
python -m unittest discover -s tests -v
```

Confirm that the test suite passes and that `output/run_metadata.json` records the expected framework version and configuration hash.

## Review questions

1. Are the stated control objectives understandable and linked to the implemented logic?
2. Are eligible populations and denominators defined without implying source completeness?
3. Do data-quality checks stop unreliable runs before exception reporting?
4. Are thresholds, weights, calendars, and other institution-specific assumptions explicit?
5. Can another practitioner reproduce the synthetic run from the documented instructions?
6. Are seeded-condition results described as regression evidence rather than production accuracy?
7. Are framework mappings cautious and free of compliance or endorsement claims?
8. Could the methodology be adapted to authorized institutional extracts after local mapping and validation?

## Useful review evidence

Useful evidence includes a public GitHub issue, pull-request review, signed memorandum, or professional email that identifies the exact release reviewed and explains the basis for the reviewer's conclusions. General praise without technical procedures carries less evidentiary value.

Independent review is not institutional adoption, regulatory approval, certification, or assurance over production performance.
