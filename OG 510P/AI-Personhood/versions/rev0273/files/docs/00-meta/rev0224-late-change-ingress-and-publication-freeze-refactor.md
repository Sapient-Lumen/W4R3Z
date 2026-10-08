# rev0224 late-change ingress and publication freeze refactor

## What this revision fixes

rev0223 could adjudicate late challenges, rollback duties, revocations, and supersessions once they were visible to the publication rollback tool. The remaining risky seam was upstream of that: a late signal could arrive as an email, correction, revocation, hash mismatch, authority withdrawal, or supersession notice and remain an informal note. Informal notes do not create replayable custody, do not prove non-host retention, and are easy to miss during recomputation.

rev0224 adds a first-class **live receipt late-change ingress record**. The object exists only to capture, retain, redact, classify, and route late signals into publication rollback adjudication. It cannot continue a published snapshot, cannot preserve reliance, cannot upgrade reliance, and cannot increment the live floor.

## Current route

`evidence drop -> pilot -> LEAP candidate -> candidate challenge/replay -> custody authority gate -> custody record -> response verification gate -> response record -> intake conversion gate -> intake record -> import readiness gate -> actual import gate -> floor activation record -> quorum participation record -> computed floor -> floor recompute receipt -> publication rollback adjudication -> late-change ingress`

The final arrow is intentionally not a new reliance gate. It is a reopening gate. If a genuine live signal appears, the late-change ingress freezes continuation and forces a new floor recompute receipt plus publication rollback adjudication. A no-signal monitoring record has no publication effect.

## New executable surfaces

- `tools/prepare_live_receipt_late_change_ingress_record.py`
- `tools/audit_live_receipt_late_change_ingress_record.py`
- `schemas/live-receipt-late-change-ingress-record.schema.json`
- `examples/live-receipt-late-change-ingress-record-rev0224-no-signal-monitoring.json`
- `fixtures/negative-tests/late-change-ingress-unretained-signal-continued.json`
- `fixtures/negative-tests/late-change-ingress-private-vault-leak.json`
- `fixtures/negative-tests/late-change-ingress-supersession-not-routed.json`

## Safety rule

Any live challenge, revocation, supersession, rollback evidence, correction, authority withdrawal, or hash mismatch that appears after publication must become a late-change ingress object before anyone can claim the published posture was rechecked. The ingress object itself always has `no_direct_floor_effect: true`; it is a freeze and routing surface, not a floor or reliance source.

## Audit/refactor note

The admission graph and import invariant report now include the late-change ingress boundary. Release-critical lint runs the late-change ingress audit alongside the publication rollback audit, so late signals cannot be reintroduced as off-ledger notes without failing the active handoff path.

## Remaining risk

The archive still has no genuine external artifact or genuine late counterparty signal. The next substantive step remains a deliberately small real artifact pilot. This revision reduces the risk that a future late revocation or supersession will be missed after a clean-looking publication snapshot.
