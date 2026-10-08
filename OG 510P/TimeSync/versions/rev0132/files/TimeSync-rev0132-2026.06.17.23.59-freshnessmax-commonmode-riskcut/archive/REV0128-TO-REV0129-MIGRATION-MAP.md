# rev0128 to rev0129 migration map

## Added

- `tools/ntpq_adapter.py`
- `examples/ntpq/rv-normal.txt`
- `examples/ntpq/peers-normal.txt`
- `examples/ntpq/rv-leap-unsync.txt`
- `examples/ntpq/rv-high-distance.txt`
- `examples/ntpq/rv-missing-rootdisp.txt`
- `tests/ntpq-adapter-golden.yaml`
- `tests/rfc9249-ntpq-observation-crosswalk.yaml`
- `examples/evaluator/ntpq-p1-general-satisfied.json`
- `evaluator/NTPQ-REFERENCE-EVALUATOR-REV0129.md`

## Changed

- `tools/validate_archive.py` now runs the ntpq adapter self-test.
- `tools/rfc9249_crosswalk.py` now validates both chrony and ntpq crosswalks.
- `tools/chrony_policy.py` now supports adapter-family policy IDs while preserving the chrony default.
- `evaluator/p1-chrony-policy.json` now declares adapter policy IDs and removes the old blanket non-chrony limitation.

## Compatibility

Existing chrony examples and outputs remain valid. The TimeState core and published schemas are unchanged.
