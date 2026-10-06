# Cloudtainer forward momentum — rev0197 — open/bucket close-abort lifecycle refactor

Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal. Linked rev0197 is runtime lifecycle work, not a promotion.

## Risk selected

After rev0196, close-owned cancellation reached queued Web Lock acquisition and acquired provider calls. The next risk was lower: raw OPFS `open()` / prefix / digest-bucket directory acquisition still had gaps where close could flip state while directory handles continued to advance until a later staged-write checkpoint. Guarded `open()` also ignored provider options, so a close-composed signal could protect lock acquisition but not underlying store open.

## Change

- Raw `OpfsAsyncBlockStore.open(options)` now participates in the same lifecycle operation envelope as get/put/delete and checks the close-composed `AbortSignal` around origin-root and prefix directory acquisition.
- Mutable digest-bucket acquisition now accepts `{ signal, op }` and rechecks abort before/after bucket directory steps before staged/final block files are created.
- `WebLockGuardedBlockStore.open(options)` now forwards provider options to `store.open(providerOptions)` so close can abort acquired open providers as well as put/get/etc.
- Existing close-abort probes and contract audits were extended rather than adding a new registry slice.

## Validation

- `node tools/run_tests.mjs --tier full --id opfs:block-store-close-abort-inflight-proof,facility:opfs-block-store-close-abort-inflight-contract-audit,storage:web-lock-guarded-close-abort-proof,facility:web-lock-guarded-close-abort-contract-audit --jobs 1 --json artifacts/validation/REV0125-CLOSE-ABORT-LIFECYCLE-RUN.json`
- `node tools/package_tarball_boundary_contract_audit.mjs --json artifacts/audit/REV0125-PACKAGE-TARBALL-BOUNDARY-CONTRACT-AUDIT.json`
- `python3 tools/check_cube.py`

## Research posture

MDN continues to describe OPFS as origin-private but quota-bound; StorageManager estimates are advisory. Web Locks support aborting queued requests via `AbortSignal`, and the W3C spec says abort is ignored after a lock is granted, so BrowserRT must separately pass close-composed provider signals after acquisition.

## Non-claims

No runtime promotion, package publication, production readiness, quota reservation, eviction survival, fsync durability, Storage Buckets support, Web Lock fairness, Service Worker lifetime, crash recovery, browser-kill recovery, or cross-browser proof. Some browser directory calls may complete before the next cooperative abort checkpoint; the claim is bounded lifecycle fencing before staged/final file mutation, not preemptive cancellation of the browser’s internal OPFS operation.
