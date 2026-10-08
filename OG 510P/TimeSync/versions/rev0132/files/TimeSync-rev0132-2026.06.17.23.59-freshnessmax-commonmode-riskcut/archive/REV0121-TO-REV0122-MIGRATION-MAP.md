# rev0121 to rev0122 migration map

## Summary

rev0121 identified the missing real-adapter/reference-evaluator proof. rev0122 starts that proof with a chrony replay adapter and a P1 reference evaluator.

## Added

- `tools/chrony_adapter.py`
- `examples/chrony/`
- `tests/chrony-adapter-golden.yaml`
- `examples/evaluator/chrony-p1-general-satisfied.json`
- `examples/evaluator/chrony-p1-general-stale-fallback.json`
- `evaluator/chrony-p1-general-explanation.json`
- `evaluator/CHRONY-REFERENCE-EVALUATOR-REV0122.md`
- `AUDIT-2026.06.17-rev0122.md`
- `archive/REV0122-AUDIT-CHRONY-ADAPTER-REFERENCE-EVAL.md`

## Changed

- `tools/validate_archive.py` now runs the chrony adapter golden self-test.
- `tests/semantic-test-vectors.yaml` adds `TV-122-001` and `TV-122-002`.
- Current-facing orientation and validation documents now point to the executable chrony path.
- `frontier-ticket.json` continues FT-0121 with rev0122 progress recorded instead of closing the ticket prematurely.

## Unchanged

- No TimeState field was added.
- No profile, evidence-class, transport-adapter, or JSON Schema shape changed.
- No cryptographic or named-traceability claim was introduced.
