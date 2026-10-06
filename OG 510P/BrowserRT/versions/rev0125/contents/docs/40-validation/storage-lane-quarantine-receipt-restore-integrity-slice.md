# rev0091 storage-lane quarantine receipt restore integrity slice

Current release-light task: `scheduler:storage-lane-quarantine-receipt-restore-integrity-proof`.

This slice hardens the timeout-quarantine handoff path before browser work is needed. `BlockStoreLaneAdapter.restoreTimedOutOperationQuarantineFromBlockStore()` and `BlockStoreLaneAdapter.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore()` now verify the provider-backed block reference before decoding the JSON ledger or registering a timeout-quarantine clearance receipt.

Earned behavior:

- attempts to disable verification with `verifyBeforeRestore:false` reject unless `allowUnsafeUnverifiedRestore:true` is also explicitly supplied;
- corrupt or missing persisted quarantine ledger blocks reject as `rejected-quarantine-ledger-block-integrity`;
- corrupt or missing persisted clearance receipt blocks reject as `rejected-clearance-receipt-block-integrity`;
- failed block verification returns before `get()`, JSON decode, ledger import, or clearance receipt registration;
- valid restored clearance receipts still reject stale pre-clearance timeout-quarantine replay;
- valid restored quarantine ledgers still force storage-lane backpressure.

Non-claims: unverified restore override remains unsafe and out-of-policy for normal handoff; this is provider-backed block verification, not cryptographic attestation, tamper-proof storage, provider cancellation, rollback, OPFS durability, crash safety, quota survival, eviction survival, throughput, latency SLOs, or production readiness.


This rev0091 slice explicitly treats persisted quarantine ledger and clearance receipt **block integrity** as a restore gate before any maintenance state is imported or registered.
