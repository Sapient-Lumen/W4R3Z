# Browser OPFS/Web Lock quarantine legacy-clear binding slice

`browser:opfs-web-lock-quarantine-legacy-clear-binding-proof` is the managed-Chromium counterpart to the release-light legacy-clear binding proof.

The proof boots BrowserRT in a browser page, opens a real OPFS async block store, wraps it with BrowserRT's Web Lock guarded block-store, imports a non-empty timeout-quarantine ledger, verifies the storage lane is backpressured, then exercises the legacy late-success and late-failure clear helpers. Missing or stale review fingerprints are rejected; a stale success review cannot clear a later failure row after the quarantine fingerprint changes; bound review manifests clear each row; and only then does explicit recovery allow a later guarded OPFS write to verify.

This is Managed Chromium evidence only. It does not prove cross-browser OPFS/Web Locks behavior, OPFS durability, fsync behavior, crash safety, power-loss safety, quota survival, eviction survival, provider cancellation, rollback, cryptographic ledger attestation, exactly-once semantics, automatic recovery, throughput, latency, SLOs, or production readiness.

Audit phrase: Managed Chromium real OPFS real Web Locks not cross-browser.
