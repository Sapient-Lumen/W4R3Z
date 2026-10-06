# BrowserRT rev0191 linked work

Packaged head remains `rev0125` / `0.0.125`; linked `rev0191` is not runtime promotion, semver change, publication, or production readiness.

Riskiest gap closed: after rev0190, a single staged write budgeted transient staged+final bytes correctly, but concurrent raw-store puts in the same JS realm could still each pass the same stale `StorageManager.estimate()` sample before either staged write became visible. `OpfsAsyncBlockStore` now keeps a module-level per-provider/prefix reservation ledger for passing guarded puts, includes `activeReservedBytesBefore` in projection math, and releases the reservation when the put settles.

Proof: the fake OPFS write-budget probe holds a 3000-byte staged put open with a 6000-byte transient reservation. A second 3000-byte put sees `activeReservedBytesBefore: 6000`, projects `12000` usage against a `10000` quota, rejects with `BRT_OPFS_WRITE_BUDGET_EXCEEDED`, and creates no second staged/final file. The first put then commits, cleans its staged temp, and releases the reservation to `0`.

Audit/refactor: strengthened the existing write-budget proof/contract audit and kept the current raw composite AbortSignal audit green. Restored compact type needles required by carried audits instead of widening budgets or opening a new registry slice.

Non-claims: same-realm reservation is in-process accounting, not browser quota reservation, cross-tab/cross-worker coordination, eviction survival, fsync/power-loss durability, Web Lock fairness, Storage Buckets support, Service Worker lifetime, or cross-browser proof.
