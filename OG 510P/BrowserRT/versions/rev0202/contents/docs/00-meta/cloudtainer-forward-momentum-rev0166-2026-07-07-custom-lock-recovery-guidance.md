# Rev0166 forward momentum — custom lock recovery guidance

Current office remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal. Linked revision rev0166 is a runtime failure-path hardening pass, not a runtime promotion.

## Risk taken

The remaining consumer-facing gap in the Web Lock guarded OPFS path was direct `WebLockGuardedBlockStore.withExclusive()` / `withShared()` use. Normal `put/get/has` operations already attached browser-storage recovery guidance on coordination failure; custom lock calls could still surface raw coordinator failures with less trace/recovery context.

## Change

- `src/opfs-web-lock-guarded-block-store.mjs` now routes custom lock failures through `#customLockError()`.
- Custom failures increment guarded-store error stats, attach `createBrowserStorageRecoveryGuidance()` / `attachBrowserStorageRecoveryGuidance()`, and emit `storage:opfs-web-lock-guard-custom-error` plus `storage:opfs-web-lock-guard-recovery-guidance`.
- `withExclusive()` / `withShared()` now emit the same start/end and abort-signal trace families as built-in operations.
- `tools/web_lock_guarded_abort_signal_probe.mjs` proves an abortSignal-only queued `withShared()` rejects before callback/provider mutation with `BRT_WEB_LOCK_ABORTED` recovery guidance.
- `tools/web_lock_guarded_abort_signal_contract_audit.mjs` now guards the custom recovery trace and compact impact-map coverage.

## Audit/refactor note

The retained proof artifact was compacted while adding the new custom-lock checks, keeping this turn inside the cloudtainer source budget instead of growing another broad report.

## Non-claims

No runtime promotion, package publication, semver change, OPFS quota reservation, eviction-survival proof, fsync/power-loss durability, crash recovery, Service Worker lifetime guarantee, Web Lock fairness/starvation-freedom guarantee, cross-browser guarantee, production readiness, production retry authorization, or browser-light managed-lifecycle claim.
