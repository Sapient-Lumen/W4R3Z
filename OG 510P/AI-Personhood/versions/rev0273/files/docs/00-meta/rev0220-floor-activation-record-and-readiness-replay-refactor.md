# rev0220 floor activation record and readiness replay refactor

rev0220 closes the next live-evidence overclaim seam: an `actual-live-import` gate could previously carry a linked import-readiness reference as a string and still look like a computed-floor candidate. That is too weak for the archive's central anti-laundering posture. A string ref is not a replayed object, and a positive import-gate claim is not yet a floor movement.

## Risk corrected

The risky path was:

`intake record -> import readiness gate -> actual import gate -> computed floor`

rev0219 made the import-readiness reference mandatory on actual import gates. rev0220 adds the missing replay and activation boundary: the floor engine must now be able to load and verify the referenced import-readiness gate object, confirm that the readiness gate matches the same intake/response/custody/LEAP lineage, confirm that readiness authorized only actual import-gate preparation, and then load a separate live-receipt-floor activation record before the import gate can enter floor recomputation.

## New boundary

The enforced path is now:

`evidence drop -> pilot -> LEAP candidate -> challenge/replay -> custody authority gate -> custody record -> response verification gate -> response record -> intake conversion gate -> intake record -> import readiness gate -> actual import gate -> floor activation record -> computed floor`

The floor activation record is a final pre-compute replay receipt. It checks readiness replay, cryptographic adapter binding, signature payload replay, request trace replay, non-host retention, sealed/public parity, duplicate counterparty and dependency-group checks, receipt-class duplicate checks, supersession, challenge/rollback state, failed-gate summary readiness, manual override absence, and private-material release safety.

Even when the activation record is eligible, it has no direct live-floor effect. It can only admit an import gate to the computed-floor candidate set. The floor engine must still recompute class-local quorum, independence, and required receipt classes.

## Implementation surfaces

rev0220 adds:

- `schemas/live-receipt-floor-activation-record.schema.json`
- `examples/live-receipt-floor-activation-record-rev0220-blocked-no-import-gate.json`
- `tools/prepare_live_receipt_floor_activation_record.py`
- `tools/audit_live_receipt_floor_activation_record.py`
- `fixtures/negative-tests/floor-activation-skipped-readiness-replay.json`
- `fixtures/negative-tests/floor-activation-manual-floor-increment.json`
- `fixtures/negative-tests/floor-activation-duplicate-supersession-ignored.json`

rev0220 also refactors:

- `tools/live_floor_lib.py`
- `tools/compute_live_receipt_floor.py`
- `tools/build_live_artifact_admission_graph.py`
- `tools/build_artifact_import_invariant_report.py`
- `schemas/live-receipt-floor-computed-snapshot.schema.json`
- `schemas/live-artifact-admission-graph.schema.json`
- `schemas/artifact-import-invariant-report.schema.json`

## What remains zero

The live receipt floor remains zero. No genuine external artifact, verified counterparty response, live intake, actual live import, floor activation, or class-local quorum is claimed. The new activation record is protective infrastructure for the first real import, not evidence that such an import exists.

## Why this is substantive rather than registry expansion

This revision changes the executable admissibility path. It makes the floor engine reject an otherwise positive import gate unless the engine can replay the readiness object and a separate floor activation object. The registry and catalog updates are secondary surfaces that point to the executable guard, not the main work.

## Next risk

The next unfinished risk is a real external artifact pilot. The path is now guarded enough that a small failed or blocked artifact run would be more useful than additional doctrine. A clean failed gate with public hash shell, private-vault custody, challenge report, and blocked downstream state would be real forward progress even if no floor movement occurs.
