# Storage-lane quarantine no-op clearance receipt guard slice — rev0080

Current release-light slice: `scheduler:storage-lane-quarantine-noop-clearance-receipt-guard-proof`.

## Risk targeted

A reviewed/scoped timeout-quarantine clear that clears zero rows is not harmless. If that no-op can still be treated as successful, maintenance code can mint a `clearanceReceipt.v1` for a still-active quarantine fingerprint and later suppress a legitimate timeout-quarantine ledger replay.

## Runtime boundary

rev0080 hardens `clearTimedOutOperationQuarantine()` and clearance-receipt creation/validation:

- zero-row clears reject as `timed-out-quarantine-clear-noop` / `rejected-noop-clear`
- `createTimedOutOperationQuarantineClearanceReceipt()` throws before minting a zero-row receipt
- `validateTimedOutOperationQuarantineClearanceReceipt()` rejects zero-cleared receipts fail-closed
- valid reviewed/scoped clearing still creates a replay-guarding receipt and permits explicit recovery

## Evidence

Run:

```bash
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-quarantine-noop-clearance-receipt-guard-proof,facility:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit --jobs 1 --json artifacts/validation/REV0080-QUARANTINE-NOOP-CLEARANCE-RECEIPT-GUARD-RUN.json
```

## Non-claims

This is browser-light synthetic-provider evidence. It does not claim provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, quota or eviction survival, cross-browser behavior, cryptographic receipt attestation, throughput, latency SLOs, or production readiness.

Exact audit marker: not provider cancellation.
