# Cloudtainer forward momentum — rev0194

Current packaged head remains `rev0125` / `0.0.125`; rev0194 is linked work only.

Risk: postured Web-Lock guarded factories installed bounded defaults, but callers could still request unbounded factory/per-operation waits.

Change: `normalizePosturedWebLockTimeoutMs()` rejects unbounded factory waits before store creation unless explicit unsafe opt-in is present. `WebLockGuardedBlockStore` exposes `allowUnboundedLockTimeoutOverride`; postured factories set it false, so per-operation `timeoutMs:0` rejects before Web Lock acquisition or OPFS mutation.

Proof: `tools/browser_storage_posture_probe.mjs` proves `BRT_BROWSER_WEB_LOCK_UNBOUNDED_TIMEOUT_REJECTED`, `BRT_OPFS_WEB_LOCK_TIMEOUT_OVERRIDE_REJECTED`, lock-inspection recovery guidance, and no fake-OPFS file creation for rejected paths.

Budget: source stayed `1449975 / 1450000` after comment-only compaction.

Non-claims: no runtime promotion, semver change, publication, Web Lock fairness, quota reservation, eviction survival, fsync durability, Service Worker lifetime, Storage Buckets support, cross-tab budget reservation, or cross-browser proof.
