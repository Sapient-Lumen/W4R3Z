# Storage-lane quarantine legacy-clear binding slice

`rev0078` hardens the older category-specific maintenance helpers:

- `clearSuccessfulTimedOutOperations()`
- `clearFailedTimedOutOperations()`

The risk was that the newer `clearTimedOutOperationQuarantine()` path was review-fingerprint-bound, while these legacy helpers still allowed a weaker reviewed/scoped clear. That created a maintenance bypass: an operator or compatibility caller could clear late-success or late-failure timeout quarantine without binding the review to the exact current quarantine fingerprint.

The release-light proof `scheduler:storage-lane-quarantine-legacy-clear-binding-proof` now checks that both legacy helpers reject missing and stale review fingerprints, clear only with a bound review manifest, keep recovery blocked after only one row is cleared, and allow explicit recovery only after all late-success/late-failure rows are reviewed and scoped against the current fingerprint.

This is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, cryptographic attestation, or production-readiness evidence.

Compatibility phrase: legacy clear helpers require review-fingerprint binding; not provider cancellation.
