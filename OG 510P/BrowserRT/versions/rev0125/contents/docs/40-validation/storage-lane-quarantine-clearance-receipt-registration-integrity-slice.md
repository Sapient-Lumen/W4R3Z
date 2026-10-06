# Storage-lane quarantine clearance receipt registration integrity slice

Revision: rev0080  
Task: `scheduler:storage-lane-quarantine-clearance-receipt-registration-integrity-proof`

This release-light slice covers a direct registration bypass in timeout-quarantine clearance receipts. A valid clearance receipt is useful because it lets BrowserRT reject stale pre-clearance quarantine ledger replay. That same surface is dangerous if a caller can directly register a forged receipt without the validation normally applied during persisted receipt restore.

The proof creates mixed late timeout outcomes, clears them with a reviewed/fingerprint-bound manifest, and then attempts direct registration of forged clearance receipts. It verifies that wrong receipt fingerprints, self-consistent but mismatched `opIds`, and `preClearanceFingerprint`/`reviewFingerprint` mismatches fail closed as `rejected-clearance-receipt-integrity`. Because rejected receipts are not installed, importing the old stale quarantine ledger still forces storage-lane backpressure. A valid directly registered receipt still rejects stale replay and leaves later writes healthy.

This is not provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, quota, eviction, throughput, SLO, or production readiness evidence. The release proof is synthetic-provider evidence only; the managed Chromium companion covers real OPFS/Web Locks behavior. Receipt fingerprints are deterministic integrity/review binding, not cryptographic attestation or tamper-proof storage.
