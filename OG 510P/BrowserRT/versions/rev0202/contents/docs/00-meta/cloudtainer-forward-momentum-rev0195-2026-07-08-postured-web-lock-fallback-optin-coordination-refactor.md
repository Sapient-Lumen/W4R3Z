# Cloudtainer forward momentum — rev0195 — postured Web-Lock fallback opt-in

Current office remains `rev0125` / `0.0.125` / OPFS Raw Composite AbortSignal. Linked rev0195 is a contract-hardening pass, not a runtime promotion.

Riskiest gap addressed: rev0194 bounded lock waits, but a caller could still set `requireWebLocks:false` on the postured guarded factory and receive an admitted guarded result even when Web Locks were unavailable. That made the safest shared-state factory too easy to use as an unlocked single-owner fallback by omission.

Change shipped: `opfsWebLockGuardedBlockStoreWithPosture()` now normalizes `lockFallbackPolicy`. With no Web Locks and `requireWebLocks:false`, it rejects before OPFS store creation unless `allowUnsafeSingleOwnerFallback:true` or an alias is explicit. Accepted fallback is labeled `admitted-single-owner-fallback`; storage-lane adapters propagate fallback policy/status; recovery guidance classifies `BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED` as pre-mutation coordination-fallback-policy.

Proof shipped: `tools/browser_storage_posture_probe.mjs` now proves both branches: default no-lock fallback rejection leaves fake OPFS empty, while explicit fallback keeps the posture-derived write-budget guard and verifies a local write. `tools/browser_storage_posture_contract_audit.mjs` gates runtime strings, recovery guidance, types, and proof coverage.

Audit/refactor: package source bytes were at the ratchet edge, so comment-only ballast in older source modules was compacted instead of widening limits. Package boundary observed: `73 / 75` files, `310267 / 350000` packed bytes, `1680217 / 1800000` unpacked bytes, `1446251 / 1450000` source bytes.

Non-claims: explicit fallback is caller-scoped single-owner mode only. It does not coordinate tabs/workers, reserve quota, ensure durability, survive eviction, prove Web Lock fairness, prove Service Worker lifetime, or establish cross-browser lifecycle behavior.
