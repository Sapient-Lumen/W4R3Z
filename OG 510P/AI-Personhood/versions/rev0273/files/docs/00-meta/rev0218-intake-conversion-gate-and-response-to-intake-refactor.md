# rev0218 — intake conversion gate and response-to-intake refactor

rev0218 closes the next live-artifact overclaim seam: a verified response record may be prepared after the response verification gate, but it still cannot become intake by implication.

## Substance

The live path now treats response-to-intake as its own explicit gate:

`evidence drop -> first-artifact pilot -> LEAP candidate -> candidate challenge/replay -> custody authority gate -> custody record -> response verification gate -> response record -> intake conversion gate -> intake record -> import gate -> computed floor`

The new intake conversion gate consumes both a response verification gate and an external receipt response record. It checks that the response gate was eligible, the response record is actual and matched to that gate, the requested receipt class matches, custody and LEAP references are bound, counterparty verification remains intact, the response is not stale or superseded, and a manual conversion review has completed.

Even when eligible, the gate allows only intake-record preparation. It does not authorize import, cross-critical quorum, or live-floor movement.

## What changed

- Added `schemas/external-receipt-intake-conversion-gate.schema.json`.
- Added `tools/prepare_external_receipt_intake_conversion_gate.py`.
- Added `tools/audit_external_receipt_intake_conversion_gate.py`.
- Added `examples/external-receipt-intake-conversion-gate-rev0218-blocked-no-response-record.json`.
- Added negative fixtures for skipped conversion gates and conversion gates that try to unlock import/floor.
- Refactored `schemas/external-receipt-response-record.schema.json` so any populated `resulting_intake_record_ref` must bind a separate `linked_intake_conversion_gate_ref`.
- Refactored `schemas/external-receipt-intake-record.schema.json` so any lineaged actual-external intake must bind `linked_intake_conversion_gate_ref`.
- Refactored the generated live-artifact admission graph and artifact import invariant report to include an explicit `INTAKE_CONVERSION_GATE` node/check.

## Why this is risk-first

The archive was close to a fake-progress trap: after rev0217, response gates were locked, but the older controlled response-to-intake drill still made it psychologically easy to treat `can_generate_actual_intake` as if it were an intake record. rev0218 makes that impossible in the live path. The response may be real; the intake still needs its own gate.

## Reliance limit

No genuine external artifact, verified live response, actual intake, import, or floor delta is claimed. The computed live receipt floor remains zero/stayed.
