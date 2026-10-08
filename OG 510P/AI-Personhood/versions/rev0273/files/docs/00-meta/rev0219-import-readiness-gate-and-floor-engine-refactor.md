# rev0219 import readiness gate and floor-engine refactor

rev0219 closes the next risky live-path seam: an actual-external intake record can no longer be routed directly into an actual receipt import gate. The new boundary is intentionally narrow. It may authorize preparation of an actual import gate, but it cannot increment the live floor, satisfy quorum, create ordinary reliance, or substitute for verifier-adapter evidence.

The enforced route is now:

`evidence drop -> first artifact pilot -> LEAP candidate -> candidate challenge/replay -> custody authority gate -> custody record -> response verification gate -> response record -> intake conversion gate -> intake record -> import readiness gate -> actual import gate -> computed floor`

The reason this matters is that intake records are tempting overclaim surfaces. They contain actual-looking state, source identity, artifact hashes, timestamps, and verification booleans. Without a separate import-readiness gate, a future operator could accidentally or deliberately treat `receipt_state=actual-external` as enough to prepare import or raise the floor. rev0219 turns that temptation into a mechanical failure mode.

The new `external-receipt-import-readiness-gate` checks that the intake conversion gate is eligible, the intake record matches the conversion gate, the receipt class and custody/LEAP lineage match, the intake's verification checks pass, non-host retained evidence exists, fixture/dry-run signals are absent, manual import-readiness review has occurred, failed-gate public summary readiness is preserved, and the next stage still requires cryptographic adapter evidence.

Even when the readiness gate passes, its downstream locks are:

- `may_prepare_actual_receipt_import_gate: true`
- `may_increment_live_floor: false`
- `live_floor_delta_allowed: false`

The actual import gate schema now requires `linked_import_readiness_gate_ref` and `linked_import_readiness_gate_verified` for `actual-live-import`. The live-floor engine also refuses to count an actual-live import unless that readiness reference and verified check are present. This moves the lock from policy prose into the counting path.

Audit/refactor actions in this revision:

- Added `tools/prepare_external_receipt_import_readiness_gate.py`.
- Added `tools/audit_external_receipt_import_readiness_gate.py`.
- Added `schemas/external-receipt-import-readiness-gate.schema.json`.
- Added `examples/external-receipt-import-readiness-gate-rev0219-blocked-no-intake-record.json`.
- Added negative fixtures for skipped intake-conversion lineage and readiness-gate floor laundering.
- Updated `schemas/actual-receipt-import-gate.schema.json` so actual-live imports require the readiness-gate reference.
- Updated `tools/live_floor_lib.py` so floor eligibility also requires the readiness-gate verification check.
- Updated the admission graph and artifact import invariant report so the new node is visible and release-checked.

The live receipt floor remains zero. The revision does not claim that an external artifact, verified response, live intake, live import, or live quorum exists.
