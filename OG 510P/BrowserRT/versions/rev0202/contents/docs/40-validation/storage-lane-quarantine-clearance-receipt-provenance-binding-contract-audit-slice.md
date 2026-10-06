# Storage-lane quarantine clearance receipt provenance binding contract audit slice

Revision: rev0092  
Task: `facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit`

This audit keeps the direct clearance-receipt provenance binding slice wired to the cube. It checks the runtime validation hooks, public validation surface, release/browser proofs, validation docs, manifest entries, impact-map entries, surface inventory entries, package scripts, Makefile targets, first-read docs, and changelog currentness.

The audit is browser-light and does not launch Chromium. The browser proof remains `browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof`.

Non-claims remain explicit: no provider cancellation, rollback, no-mutation-on-timeout, cross-browser OPFS/Web Locks behavior, OPFS durability, quota survival, eviction survival, latency/SLO claim, or production readiness claim. Receipt fingerprints are deterministic integrity/review binding, not cryptographic attestation or tamper-proof storage.


rev0082 hardening note: valid-looking clearance receipts now require registration provenance before they install replay-guard state. Bare direct registration and mismatched provenance fail closed as `rejected-clearance-receipt-provenance`. Adapter-created receipts and block-store-restored receipts carry bound provenance to the executor.


rev0092 adds audit coverage for restore-provenance block verification binding: `blockVerified`, `blockVerifyDigest`, `blockVerifyBytes`, missing-block-verify rejection, digest mismatch rejection, and byte mismatch rejection.
