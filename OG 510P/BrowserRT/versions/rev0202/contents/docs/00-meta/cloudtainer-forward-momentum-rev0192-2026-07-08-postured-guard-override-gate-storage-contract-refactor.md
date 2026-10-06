# BrowserRT rev0192 linked work

Packaged head remains `rev0125` / `0.0.125`; linked `rev0192` is not runtime promotion, semver change, publication, or production readiness.

Riskiest gap closed: after posture admission and same-realm write-budget reservations, the postured factory could still be misused by passing `writeBudgetGuard: false`. That produced an admitted posture receipt while disabling the actual OPFS put guard. Rev0192 rejects that override before store creation by default.

Proof: the storage posture probe exercises both top-level `writeBudgetGuard: false` and `storeConfig.writeBudgetGuard: false`. Both paths reject with `BRT_BROWSER_STORAGE_GUARD_OVERRIDE_REJECTED`, carry pre-mutation recovery guidance, and leave fake OPFS file count at `0`.

Audit/refactor: the storage posture contract audit now gates the override rejection policy, the public/package boundary audits still pass, and `src/types.d.ts` was indentation-compacted while preserving the installed TypeScript smoke parser's `BrowserRTRuntime` method extraction.

Non-claims: the guard override gate is a local factory contract. It is not browser quota reservation, persistent-storage grant, eviction survival, fsync/power-loss durability, Web Lock fairness, Storage Buckets support, Service Worker lifetime proof, or cross-browser proof.
