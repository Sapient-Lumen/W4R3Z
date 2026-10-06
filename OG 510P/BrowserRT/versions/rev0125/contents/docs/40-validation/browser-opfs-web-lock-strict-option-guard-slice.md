# Browser OPFS/Web Lock strict option guard slice

Rev0094 adds a managed Chromium proof for the strict Web Lock option guard. The browser proof runs the same high-risk invalid option cases in the browser realm, using real `navigator.locks.request` availability and the page's native `AbortSignal` constructor.

The proof is `browser:opfs-web-lock-strict-option-guard-proof`, implemented by `tools/browser_opfs_web_lock_strict_option_guard_probe.mjs`. It verifies BrowserRT error codes for invalid names, empty mode, string boolean controls, incompatible `ifAvailable`/`steal` combinations, incompatible cancellation options, and plain-object signals. It then runs valid exclusive/shared/ifAvailable/steal/AbortSignal/null-signal requests, performs one guarded OPFS write/verify through `WebLockGuardedBlockStore`, and confirms `navigator.locks.query()` has no held or pending rows at the end.

This proof is intentionally narrow. It is managed Chromium evidence only, not a cross-browser claim. It does not prove OPFS durability, quota behavior, eviction behavior, crash recovery, service-worker lifecycle behavior, fairness, starvation freedom, cryptographic attestation, or production readiness.
