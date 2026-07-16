# Contributing to CCAF

CCAF welcomes reproducible, nonconfidential improvements to its control logic, data-quality checks, documentation, and test coverage.

## Before contributing

- Do not submit client, employer, employee, production, or otherwise identifying data.
- Use synthetic fixtures that can be redistributed under the repository license.
- Do not describe a framework mapping as certification, compliance, examination sufficiency, or agency endorsement.
- Keep thresholds configurable and identify any assumption that requires institutional validation.
- Preserve professional review: an automated exception is a lead for investigation, not a conclusion about intent or control effectiveness.

## Proposing a control

A control proposal should identify:

1. the risk and control objective;
2. the required source records and eligible population;
3. the deterministic or statistical logic;
4. known limitations and calibration requirements;
5. a labelled synthetic condition and a negative case;
6. the expected exception schema; and
7. any cautious framework traceability.

## Local verification

```bash
python -m pip install -r requirements.txt
python run_all.py --regenerate --no-charts
python -m unittest discover -s tests -v
```

Submit focused changes with updated tests and documentation. Public discussion and review do not imply that a contributor, employer, regulator, or standards body endorses CCAF.
