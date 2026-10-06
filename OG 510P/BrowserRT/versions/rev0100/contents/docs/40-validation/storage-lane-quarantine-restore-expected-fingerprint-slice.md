# Storage-lane quarantine restore expected fingerprint slice

Task: `scheduler:storage-lane-quarantine-restore-expected-fingerprint-proof`

This release-light proof covers a handoff/maintenance confusion risk in provider-backed timeout-quarantine restore. A persisted timeout-quarantine ledger or clearance receipt can be block-integrity-valid and schema-valid while still being the wrong object for the operator's intended handoff.

The proof creates two distinct synthetic timeout-quarantine ledgers and receipts, persists both through a block-store provider, then pins restore calls to the expected quarantine/receipt fingerprints. It verifies that a valid-but-wrong ledger rejects as `rejected-quarantine-ledger-expected-fingerprint` before import, a valid-but-wrong clearance receipt rejects as `rejected-clearance-receipt-expected-fingerprint` before replay-guard registration, and a receipt with the right receipt fingerprint but wrong pre-clearance fingerprint also rejects. Matching expected fingerprints still restore normally and stale replay remains blocked.

This is intentionally not cryptographic attestation, tamper-proof storage, rollback, provider cancellation, no-mutation-on-timeout, OPFS durability, quota/eviction behavior, or production-readiness evidence.


rev0093 update: blank expected-fingerprint restore intent now fails closed before decode/import/registration; whitespace is not treated as an omitted pin. The release and Managed Chromium proofs share assertion coverage through `tools/lib/quarantine_restore_expected_fingerprint_harness.mjs`. This is still operator intent checking, not cryptographic attestation or tamper-proof storage.
