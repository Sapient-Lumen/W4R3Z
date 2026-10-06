# Storage-lane quarantine clearance receipt provenance binding slice

Revision: rev0092  
Task: `scheduler:storage-lane-quarantine-clearance-receipt-provenance-binding-proof`

This release-light slice covers a direct registration bypass in timeout-quarantine clearance receipts. A valid clearance receipt is useful because it lets BrowserRT reject stale pre-clearance quarantine ledger replay. That same surface is dangerous if a caller can directly register a receipt without or with mismatched provenance without the validation normally applied during persisted receipt restore.

The proof creates mixed late timeout outcomes, clears them with a reviewed/fingerprint-bound manifest, and then attempts direct registration of forged clearance receipts. It verifies that wrong receipt fingerprints, self-consistent but mismatched `opIds`, and `preClearanceFingerprint`/`reviewFingerprint` mismatches fail closed as `rejected-clearance-receipt-integrity`. Because rejected receipts are not installed, importing the old stale quarantine ledger still forces storage-lane backpressure. A valid directly registered receipt still rejects stale replay and leaves later writes healthy.

This is not provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, quota, eviction, throughput, SLO, or production readiness evidence. The release proof is synthetic-provider evidence only; the managed Chromium companion covers real OPFS/Web Locks behavior. Receipt fingerprints are deterministic integrity/review binding, not cryptographic attestation or tamper-proof storage.


rev0082 hardening note: valid-looking clearance receipts now require registration provenance before they install replay-guard state. Bare direct registration and mismatched provenance fail closed as `rejected-clearance-receipt-provenance`. Adapter-created receipts and block-store-restored receipts carry bound provenance to the executor.


rev0092 hardening note: `block-store-restore-clearance-receipt` provenance now has to carry a successful block verification boundary before registration is accepted: `blockVerified:true`, matching `refDigest`/`blockVerifyDigest`, matching decoded `bytes`/`blockVerifyBytes`, and adapter/store/provider source fields. Missing, digest-mismatched, or byte-mismatched restore provenance fails closed as `rejected-clearance-receipt-provenance` and does not install stale timeout-quarantine replay guard state. This is still provenance/integrity binding, not cryptographic attestation or tamper-proof storage.
