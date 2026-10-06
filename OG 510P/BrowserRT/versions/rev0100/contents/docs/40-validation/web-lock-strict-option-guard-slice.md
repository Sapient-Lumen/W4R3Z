# Web Lock strict option guard slice

Rev0094 hardens `WebLockCoordinator.request()` before it calls a browser or fake `locks.request()` implementation.

The slice closes the most dangerous option-surface gap left by the Web Lock timeout work: caller-supplied control fields are no longer passed through WebIDL/browser coercion or JavaScript truthiness. In particular, `ifAvailable: "false"` and `steal: "false"` now reject with `BRT_WEB_LOCK_OPTION_TYPE` instead of becoming true. Non-string, blank, and NUL-containing names reject with `BRT_WEB_LOCK_NAME_INVALID` before `name.includes()` can throw an accidental TypeError. Empty-string mode rejects instead of silently defaulting to exclusive. Unsupported combinations fail locally: `ifAvailable + steal`, `shared + steal`, and cancellation/timeout with `ifAvailable` or `steal`.

The release proof is `coord:web-lock-strict-option-guard-proof`, implemented by `tools/web_lock_strict_option_guard_probe.mjs`. It uses a recording fake lock manager to prove invalid names/options do not reach `locks.request()`, valid explicit false values are preserved, real `AbortSignal` is accepted, null signal remains adapter-compatible absent signal, and `coord:web-lock-option-rejected` traces/counts the local rejection path.

This is a coordinator contract proof, not a scheduling or storage durability claim. It does not prove fairness, starvation freedom, cross-browser conformance, OPFS durability, quota behavior, eviction behavior, crash recovery, cryptographic attestation, or production readiness.
