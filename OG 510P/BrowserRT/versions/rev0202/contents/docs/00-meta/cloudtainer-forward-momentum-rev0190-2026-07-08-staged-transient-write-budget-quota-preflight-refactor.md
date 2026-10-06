# BrowserRT rev0190 linked work

Packaged head remains `rev0125` / `0.0.125`; linked `rev0190` is not runtime promotion, semver change, publication, or production readiness.

Riskiest gap closed: staged OPFS writes previously budgeted only final block bytes even though the provider can temporarily hold staged + final bytes. `OpfsAsyncBlockStore` now budgets guarded staged puts with `transientWriteMultiplier` / `transientOverheadBytes` before OPFS open/file creation. `buildBrowserStorageAdmissionPolicy()` carries the same math into `plannedBudgetedBytes`, and `opfsAsyncBlockStoreWithPosture()` exposes that rejection detail.

Proof: a fake 4096-byte put budgets 8192 transient bytes and rejects with zero OPFS file creation; a planned 600-byte posture admission budgets 1200 bytes and rejects against 500 projected writable bytes. Existing probes/audits were strengthened, not replaced with a registry slice.

Non-claims: no quota reservation, eviction survival, fsync/power-loss durability, Web Lock fairness, Storage Buckets support, Service Worker lifetime guarantee, or cross-browser guarantee.
