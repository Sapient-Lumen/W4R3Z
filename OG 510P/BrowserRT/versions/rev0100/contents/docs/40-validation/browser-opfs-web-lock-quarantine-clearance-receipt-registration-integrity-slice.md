# Browser OPFS/Web Lock quarantine clearance receipt registration integrity slice

Revision: rev0080  
Task: `browser:opfs-web-lock-quarantine-clearance-receipt-registration-integrity-proof`

This managed Chromium proof exercises the direct clearance-receipt registration guard against real guarded OPFS/Web Locks. The page creates two real OPFS writes that exceed the storage-lane operation timeout, later settle as one success and one failure, and are then cleared with a reviewed/fingerprint-bound manifest.

The proof then uses fresh storage-lane adapters over the same guarded OPFS store. Direct registration of forged receipts is rejected before replay guard state is installed. The stale pre-clearance ledger therefore still imports and forces backpressure after forged registration attempts. A valid direct registration still works: the stale ledger replay is rejected as `rejected-cleared-quarantine-replay`, the lane remains healthy, the original OPFS blocks verify, and a later guarded OPFS write verifies. Final Web Lock state drains to zero.

Managed Chromium only. This is not cross-browser OPFS/Web Locks behavior, not provider cancellation, not rollback, not no-mutation-on-timeout, not OPFS durability, not quota or eviction survival, and not production readiness. Receipt fingerprints are deterministic integrity/review binding rather than cryptographic attestation or tamper-proof storage.
