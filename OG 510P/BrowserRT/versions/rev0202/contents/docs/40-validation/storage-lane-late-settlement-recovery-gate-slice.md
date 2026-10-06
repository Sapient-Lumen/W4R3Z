# Storage-lane late-settlement recovery-gate slice

Revision: rev0069  
Task: `scheduler:storage-lane-late-settlement-recovery-gate-proof`  
Current role: browser-light release guard for the late provider settlement gate.

## Purpose

A bounded storage-lane operation timeout is useful only if BrowserRT keeps tracking the provider operation that timed out. The risky case is a provider that mutates storage, the scheduler times out, and then explicit recovery reopens the lane while that old provider promise is still unresolved.

This slice proves the release-tier boundary: `BRT_STORAGE_OPERATION_TIMEOUT` marks the lane unhealthy, the timed-out operation remains visible as an unsettled provider operation, and `recoverWhenStoreSettled()` refuses to reopen the lane until late provider settlement drains.

## Evidence shape

`tools/storage_lane_late_settlement_recovery_gate_probe.mjs` uses a synthetic block store that commits bytes before settlement, then holds the provider promise open. The proof checks:

- `storage-lane:operation-timeout-unsettled` is emitted when the operation times out.
- The executor snapshot reports one `unsettledTimedOutOperationCount`.
- `recoverWhenStoreSettled()` returns `timed-out-operation-still-unsettled` even though the store coordination surface itself reports settled.
- `storage-lane:late-provider-settlement` is emitted after explicit release.
- The failed timed-out operation is not retroactively published as a successful adapter result.
- Later writes complete only after explicit recovery.

## Non-claims

This is not provider cancellation, not provider interruption, not rollback, not no-mutation evidence, not exactly-once evidence, and not production readiness. The proof intentionally allows the provider mutation to exist before settlement so that recovery gating does not confuse timeout with cancellation.

Cross-browser, quota, eviction, and crash behavior are out of scope for this browser-light slice.
