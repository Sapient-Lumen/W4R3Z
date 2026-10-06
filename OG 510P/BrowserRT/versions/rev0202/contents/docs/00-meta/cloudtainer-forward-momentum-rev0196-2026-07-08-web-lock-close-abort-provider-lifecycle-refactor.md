# rev0196 forward momentum — Web-Lock close abort / provider lifecycle refactor

Runtime head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal. Linked rev0196 is a lifecycle contract pass, not runtime promotion.

Risk fixed: guarded Web-Lock stores could be closed while a put/get/delete was queued for a lock or already inside the provider. Close changed the local `closed` flag, but it did not own an AbortSignal wired into lock acquisition and provider options. A queued operation could therefore wait until timeout rather than close, and an acquired provider call did not receive a close-owned abort by default.

Substance shipped: `WebLockGuardedBlockStore` now owns a close `AbortController`, composes its signal into guarded operation lock/provider options, re-checks closed state after lock acquisition, aborts the signal on `closeAsync`, and exposes `closeSignalAborted` / `closeAbortSignals`. `WebLockCoordinator` now preserves abort reason provenance (`abortReasonCode`) for pre-acquisition aborts so close-owned cancellation is not mislabeled as a generic caller abort.

Proof: `storage:web-lock-guarded-close-abort-proof` covers both paths: close aborts a queued lock request before a 5s timeout can win with zero provider puts, and close aborts an already-acquired provider signal with `BRT_OPFS_WEB_LOCK_GUARD_CLOSED`.

Audit/refactor: `facility:web-lock-guarded-close-abort-contract-audit` gates the close controller, signal wiring, post-acquisition closed-state check, coordinator abort provenance, manifest registration, and package scripts.

Non-claims: same-object close cancellation is not Web Lock fairness, cross-tab quota reservation, OPFS durability, eviction survival, crash recovery, Service Worker lifetime, or cross-browser proof.
