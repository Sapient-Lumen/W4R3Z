# Uncertainty / significance / coverage stop rule

`OQ-0112` blocks interval, p-value, sigma, discovery, exclusion, calibration, and coverage wording unless three rows are current:

- `UNCERTAINTY-INTERVAL-LEDGER.json`
- `SIGNIFICANCE-THRESHOLD-LEDGER.json`
- `COVERAGE-CALIBRATION-LEDGER.json`

A route must declare what interval was constructed, which statistic was tested, what threshold convention was used, and whether nominal coverage or posterior calibration has been stress-tested.

Passing any one of those rows only controls statistical wording. It does not promote a route.
