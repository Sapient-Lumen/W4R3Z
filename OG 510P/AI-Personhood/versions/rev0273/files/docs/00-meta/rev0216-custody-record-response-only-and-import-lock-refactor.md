# rev0216 custody-record response-only and import-lock refactor

rev0216 closes the next overclaim seam after the custody authority gate. Before this revision, the archive had a custody-record schema that could too easily imply that once custody existed, response, intake, and import readiness traveled together. That was too broad for the first real artifact path.

The new rule is narrower and safer: **custody can authorize response preparation only**. It cannot create an intake record, cannot run an actual-receipt-import-gate, and cannot move the computed live receipt floor. A custody object is now a raw-artifact/authority binding, not a receipt.

## What changed

The revision adds `tools/prepare_counterparty_artifact_custody_record.py`. The tool consumes a custody authority gate and, when the gate is eligible, rereads the external private vault, rechecks hash and size against the candidate challenge report, and emits a counterparty-artifact custody record. If the gate is pending, blocked, unscoped, or the vault reread fails, the tool emits a quarantined custody record instead of fabricating progress.

The custody record schema now requires `linked_custody_gate_ref`. For `live-candidate-artifact` custody records, the schema requires a response-only posture:

- `may_create_response_record: true`
- `may_create_intake_record: false`
- `may_run_import_gate: false`
- `live_import_floor_delta: 0`
- `live_reliance_effect: stayed`

This is a deliberate split. The next object may be an external receipt response, but only after custody has passed. Intake, import, verifier-adapter binding, challenge/rollback, class-local replay, independence discount, and computed-floor recomputation remain separate downstream gates.

## New audit/refactor surface

`tools/audit_counterparty_custody_response_lock.py` runs the full synthetic route:

1. first-artifact pilot into an external private vault,
2. candidate challenge/replay with private-vault reread,
3. custody authority gate,
4. custody record preparation,
5. schema probes proving that ungated custody and custody-unlocked intake/import both fail.

The audit also proves that blocked gates produce only quarantined custody records, eligible synthetic custody records do not leak raw private bytes, and the custody tool does not generate response, intake, or import objects.

## Negative fixtures added

Two new negative fixtures protect the refactor:

- `custody-record-live-candidate-without-gate-ref.json`
- `custody-record-unlocks-intake-import.json`

These target the two most likely shortcuts: creating a live-candidate custody record from hash custody alone, and treating custody as permission to skip response reconciliation and go straight to intake/import.

## Current live-floor state

The live receipt floor remains zero. rev0216 makes the first real artifact path safer and more executable, but no genuine external artifact is claimed and no custody record in the checked-in corpus is admitted as a live receipt.
