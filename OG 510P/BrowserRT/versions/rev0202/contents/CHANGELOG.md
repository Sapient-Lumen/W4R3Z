## rev0125 — 2026-06-18 — Guarded staged recovery serialization

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal.
- Current proof anchors remain `opfs:block-store-raw-composite-abort-signal-proof`, `browser:opfs-block-store-raw-composite-abort-signal-proof`, and `facility:opfs-block-store-raw-composite-abort-signal-contract-audit`.
- Current runtime terms intentionally retained for audits: `OpfsAsyncBlockStore`, `abortSignal`, `signal`, opfsasyncblockstore, OPFS, Web Locks, composite, browser-light.
- Current non-claims remain visible: no production runtime, no package publication, no production readiness, no cross-browser guarantee, no persistent storage grant, no quota reservation, no eviction survival, no fsync or power-loss durability claim, no general crash recovery, no Web Lock fairness/starvation-freedom guarantee, and browser-light validation is not managed-browser lifecycle proof.
- Historical quarantine/recovery anchors retained for carried audits: `late-failure-clear-review-required`, `late-failure-clear-scope-required`, storage-lane, timed-out quarantine, provider abort, digest/prefix verification, and recovery review.

## rev0202 linked work — 2026-07-08 — Runtime-core recovery guidance table / ratchet

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0202 is linked work only.
- Substance: `src/browser-storage-recovery-guidance.mjs` now table-drives recovery steps and code classification instead of carrying duplicated switch/if branches in the runtime-core closure.
- Audit/refactor: `tools/runtime_core_entry_contract_audit.mjs` ratchets runtime-core from 130,000 to 128,500 bytes after the closure dropped from 129,576 to 128,028 bytes.
- Package boundary observed: package `src` is 1,393,791 / 1,450,000 bytes, package examples remain 218,374 / 220,000 bytes, and the explicit package source allowlist remains green.
- Research posture: OPFS quota/site-data deletion, Web Locks post-grant AbortSignal limits, Storage Buckets capability branching, and OPFS byte-time privacy risk remain explicit non-claims/gates.
- Non-claim: no runtime promotion, publication, root facade split, quota reservation, eviction survival, fsync durability, Storage Buckets support, Web Lock fairness, privacy guarantee, or cross-browser proof.

## rev0201 linked work — 2026-07-08 — Package src allowlist / storage privacy review

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0201 is linked work only.
- Substance: package `src` publishing now uses an explicit public/runtime/dynamic-worker closure allowlist instead of broad `src/*.mjs` / `src/*.d.ts` globs.
- Runtime posture: browser storage posture gained an advisory `storage-timing-side-channel-review` path for large planned OPFS writes, grounded in current OPFS/FROST research without claiming mitigation.
- Audit/refactor: package boundary, public API, runtime-core, and browser storage posture audits/probes were updated to enforce the allowlist and privacy review path.
- Package boundary observed: package `src` dropped from 1,448,605 to 1,395,339 bytes; file count dropped from 73 to 63; runtime-core remained 129,576 / 130,000 bytes.
- Non-claim: no runtime promotion, publication, root facade split, quota reservation, eviction survival, fsync durability, Storage Buckets support, Web Lock fairness, privacy guarantee, or cross-browser proof.

## rev0200 linked work — 2026-07-08 — Package examples budget ratchet / refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0200 is linked work only.
- Substance: `examples/runtime-core-consumer.mjs` now shares lane/encoder setup, and the browser OPFS examples share repeated postured-storage proof predicates.
- Audit/refactor: `tools/package_tarball_boundary_contract_audit.mjs` ratchets package examples from 225,000 to 220,000 bytes and self-checks the ratchet string.
- Packaging harness: `tools/package_release.py` now stamps `package_stamp` / `package_timestamp` with the filename timestamp, preventing linked package metadata split-brain.
- Package boundary observed: examples moved from 224,836 / 225,000 bytes to 218,374 / 220,000 bytes; runtime-core stayed 6 files / 128,439 bytes.
- Research posture: OPFS quota/site-data deletion, Web Locks post-grant cancellation limits, Storage Buckets capability branching, and OPFS byte-time privacy risk remain explicit non-claims/gates.
- Non-claim: no runtime promotion, publication, root facade split, quota reservation, eviction survival, fsync durability, Storage Buckets support, Web Lock fairness, privacy guarantee, or cross-browser proof.

## rev0199 linked work — 2026-07-08 — Runtime-core product-wedge decoupling / budget refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0199 is linked work only.
- Substance: `browserrt/runtime-core` no longer imports or exports the product-wedge proof helper; the consumer example now emits a compact runtime-core receipt locally.
- Audit/refactor: the runtime-core entry audit now forbids `src/product-wedge.mjs` closure drift and proves 6 files / 128,439 bytes under the 130,000-byte ratchet.
- Cloudtainer waste correction: the inactive-evidence markdown table was compacted to a JSON-receipt pointer instead of duplicating rows.
- Research posture: OPFS quota/site-data deletion, persistence, Web Locks grant lifecycle, Storage Buckets capability branching, and FROST-style OPFS byte-time privacy risk remain non-claims/gates.
- Non-claim: no runtime promotion, publication, root facade split, quota reservation, eviction survival, fsync durability, Storage Buckets support, Web Lock fairness, privacy guarantee, or cross-browser proof.

## rev0198 linked work — 2026-07-08 — Mission/waste deep-read correction map

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0198 is linked analysis only.
- Heart: BrowserRT is a boring browser-local mutation kernel: bounded admission, cancellable provider calls, same-origin OPFS/Web Lock coordination, receipts, and honest storage non-claims.
- Missing: tiny runtime-core package split, OPFS IO/privacy posture, cross-browser capability table, Storage Buckets posture branch, readable source posture, and one user-value local-first demo.
- Waste diagnosis: proof-product inversion, active-cube byte pressure, package boundary margins at the edge, and source readability sacrificed to budget.
- Correction order: split runtime/evidence, archive historical verbose proof out-of-tree, add byte-time guard, surface storage posture receipts, classify browser support, and compact only generated package output.
- Non-claim: no runtime promotion, package publication, production readiness, quota reservation, eviction survival, fsync durability, Storage Buckets support, privacy guarantee, Web Lock fairness, or cross-browser proof.

## rev0197 linked work — 2026-07-08 — Open/bucket close-abort lifecycle refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0197 is linked work only.
- Substance: raw OPFS open/prefix/bucket acquisition now shares the close-composed operation `AbortSignal`, and guarded `open(options)` forwards provider options to the underlying store.
- Runtime behavior: close during mutable digest-bucket acquisition rejects with `BRT_OPFS_OPERATION_ABORTED` before staged/final file creation; guarded open can propagate `BRT_OPFS_WEB_LOCK_GUARD_CLOSED` through the acquired provider signal.
- Audit/refactor: existing close-abort proof/audit were extended instead of adding a registry family; package source budget stayed under the existing ratchet after compacting the new helper path.
- Package boundary observed: see `REV0197-LINKED-REVISION-RECEIPT.json` for current pack numbers.
- Non-claim: close abort is cooperative lifecycle fencing; it is not browser-internal OPFS preemption, Web Lock fairness, quota reservation, eviction survival, fsync durability, crash recovery, Storage Buckets support, or cross-browser proof.


## rev0196 linked work — 2026-07-08 — Web-Lock close abort / provider lifecycle refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0196 is linked work only.
- Substance: guarded Web-Lock stores now own a close `AbortController` and compose its signal into lock acquisition plus provider options.
- Runtime behavior: close aborts queued lock acquisition before long timeouts can win, aborts acquired provider signals, re-checks closed state after lock acquisition, and exposes `closeSignalAborted` / `closeAbortSignals`.
- Recovery provenance: `WebLockCoordinator` preserves `abortReasonCode`, so close-owned pre-acquisition aborts retain `BRT_OPFS_WEB_LOCK_GUARD_CLOSED` instead of looking like a generic caller abort.
- Audit/refactor: new close-abort proof covers queued and acquired paths; contract audit gates signal wiring, closed-state recheck, abort provenance, manifest registration, and scripts.
- Package boundary observed: `73 / 75` files, `310383 / 350000` packed bytes, `1681807 / 1800000` unpacked bytes, `1447972 / 1450000` source bytes.
- Non-claim: close-owned cancellation is same-object lifecycle hygiene only; it is not Web Lock fairness, cross-tab quota reservation, OPFS durability, eviction survival, Service Worker lifetime, Storage Buckets support, crash recovery, or cross-browser proof.


## rev0195 linked work — 2026-07-08 — Postured Web-Lock fallback opt-in / coordination refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0195 is linked work only.
- Substance: postured Web-Lock-guarded OPFS factories reject unlocked no-Web-Locks fallback before OPFS store creation unless the caller explicitly opts into unsafe single-owner fallback.
- Runtime behavior: `requireWebLocks:false` without `allowUnsafeSingleOwnerFallback:true` now throws `BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED`; explicit fallback returns `status: admitted-single-owner-fallback` and a `lockFallbackPolicy` while preserving posture-derived write-budget guards.
- Recovery guidance: fallback rejection is classified as pre-mutation `coordination-fallback-policy`, with recovery steps requiring Web Locks/coordinator double or explicit unsafe single-owner fallback opt-in.
- Audit/refactor: posture proof covers no-lock rejection and labeled explicit fallback; storage posture contract audit gates fallback policy, type surface, recovery guidance, and probe coverage; comment-only source ballast was compacted rather than widening budgets.
- Package boundary observed: `73 / 75` files, `310267 / 350000` packed bytes, `1680217 / 1800000` unpacked bytes, `1446251 / 1450000` source bytes.
- Non-claim: explicit fallback is caller-scoped single-owner mode only; it is not same-origin coordination, Web Lock fairness, quota reservation, OPFS durability, eviction survival, Service Worker lifetime, Storage Buckets support, or cross-browser proof.


## rev0194 linked work — 2026-07-08 — Postured Web-Lock timeout override gate / coordination refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0194 is linked work only.
- Substance: postured Web-Lock-guarded OPFS factories reject unbounded `lockTimeoutMs:0` / `lockContentionTimeoutMs:0` before store creation unless the caller explicitly opts into unsafe unbounded waits.
- Runtime behavior: admitted postured guarded stores reject per-operation `{ timeoutMs: 0 }` before Web Lock acquisition and OPFS mutation; `allowUnboundedLockTimeoutOverride:false` is visible in guarded snapshots.
- Recovery guidance: `BRT_BROWSER_WEB_LOCK_UNBOUNDED_TIMEOUT_REJECTED` and `BRT_OPFS_WEB_LOCK_TIMEOUT_OVERRIDE_REJECTED` are classified as pre-mutation posture-lock-policy failures with lock-inspection guidance.
- Audit/refactor: storage posture proof covers factory-level and per-operation unbounded wait rejections; package boundary remains under the source ratchet after comment-only compaction.
- Package boundary observed: `73 / 75` files, `312538 / 350000` packed bytes, `1684548 / 1800000` unpacked bytes, `1449975 / 1450000` source bytes.
- Non-claim: bounded lock-wait posture is local BrowserRT admission policy; it is not Web Lock fairness, cross-tab quota reservation, OPFS durability, eviction survival, Service Worker lifetime, Storage Buckets support, or cross-browser proof.


## rev0193 linked work — 2026-07-08 — Postured per-put guard override gate / budget refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0193 is linked work only.
- Substance: admitted postured stores reject disabled or weaker per-put `writeBudgetGuard` / `minFreeBytesForPut` / `maxUsageRatioForPut` overrides before OPFS mutation while allowing same-or-stronger guard reiteration.
- Runtime behavior: postured factories set `allowWriteBudgetGuardOverride:false`; rejected writes use `BRT_OPFS_WRITE_BUDGET_OVERRIDE_REJECTED`, carry override keys/comparison detail, and recovery guidance reports `mutationAttempted:false`.
- Audit/refactor: posture proof covers raw postured and Web-Lock guarded override attempts; existing staged/reservation guard proof remains green; source comment ballast was compacted instead of widening budgets.
- Package boundary: `73 / 75` files, `313208 / 350000` packed bytes, `1683518 / 1800000` unpacked bytes, `1448748 / 1450000` source bytes.
- Non-claim: the gate is a local postured-store invariant only; it is not browser quota reservation, cross-tab/cross-worker coordination, eviction survival, fsync durability, Storage Buckets support, Web Lock fairness, or cross-browser proof.


## rev0192 linked work — 2026-07-08 — Postured guard override gate / storage contract refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0192 is linked work only.
- Substance: postured OPFS factories reject explicit `writeBudgetGuard` overrides before OPFS store creation unless the caller opts into unsafe override policy.
- Runtime behavior: rejected attempts use `BRT_BROWSER_STORAGE_GUARD_OVERRIDE_REJECTED`, emit `storage:opfs-block-store-posture-guard-override-rejected`, carry pre-mutation recovery guidance, and admitted results expose `postureGuardPolicy`.
- Audit/refactor: storage posture proof covers both top-level and `storeConfig` guard-disable attempts; package boundary and installed consumer smoke stay green after compact type indentation.
- Package boundary: `73 / 75` files, `314412 / 350000` packed bytes, `1683975 / 1800000` unpacked bytes, `1449240 / 1450000` source bytes.
- Non-claim: the guard override gate is a local postured-factory contract; it is not browser quota reservation, cross-tab/cross-worker coordination, eviction survival, fsync durability, Storage Buckets support, or cross-browser proof.


## rev0191 linked work — 2026-07-08 — Same-realm write-budget reservation / stale-estimate refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0191 is linked work only.
- Substance: `OpfsAsyncBlockStore` now reserves passing write-budget preflight bytes per provider/prefix in the current JS realm until the guarded put settles.
- Runtime behavior: projected usage includes `activeReservedBytesBefore`; passing receipts carry `sameRealmReservation` and `reservation`, snapshots expose `activeWriteBudgetReservedBytes`, and stats record reservation start/settle/high-water counts.
- Audit/refactor: existing write-budget and raw-composite audits were strengthened; the proof holds a 3000-byte staged put open, proves a second 3000-byte put sees the first 6000-byte transient reservation and rejects before creating another file, then proves reservation release to `0`.
- Package boundary: `73 / 75` files, `313304 / 350000` packed bytes, `1680423 / 1800000` unpacked bytes, `1445688 / 1450000` source bytes.
- Non-claim: same-realm reservation is conservative in-process accounting only; it is not browser quota reservation, cross-tab/cross-worker coordination, eviction survival, fsync durability, Storage Buckets support, or cross-browser proof.

## rev0190 linked work — 2026-07-08 — Staged transient write-budget quota preflight

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0190 is linked work only.
- Substance: OPFS write-budget guards now account for staged-write transient bytes (`transientWriteMultiplier`, default `2`) before OPFS open/file creation, so staged + final block pressure is checked before mutation.
- Runtime behavior: `writeBudgetGuard` returns `budgetedBytes` and `transientStagingBytes`; postured storage admission turns caller `plannedWriteBytes` into `plannedBudgetedBytes` and carries that into `BRT_BROWSER_STORAGE_ADMISSION_REJECTED` detail.
- Audit/refactor: existing write-budget/posture probes and contract audits were strengthened instead of creating a new registry slice; fake OPFS proves `4096` requested bytes budget as `8192` transient bytes and reject before files are created.
- Package boundary: `73 / 75` files, `312188 / 350000` packed bytes, `1675469 / 1800000` unpacked bytes, `1440961 / 1450000` source bytes.
- Non-claim: transient staged-byte preflight uses advisory `StorageManager.estimate()`; it is not quota reservation, eviction survival, fsync durability, Storage Buckets support, or cross-browser proof.

## rev0189 linked work — 2026-07-08 — Planned-write admission preflight / type budget refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0189 is linked work only.
- Substance: storage admission policy now accepts caller-sized planned write aliases and reports `plannedWriteBytes` / `plannedWriteFits`.
- Runtime behavior: postured OPFS factory creation rejects with `reject-planned-write-over-budget` before store creation when the expected batch exceeds projected writable budget.
- Audit/refactor: posture probe proves 600 planned bytes reject against 500 projected writable bytes with no fake-OPFS files created; `src/types.d.ts` comment-tail compaction kept package src under budget without widening guards.
- Non-claim: planned-write preflight uses advisory `StorageManager.estimate()`; it is not quota reservation, eviction survival, fsync durability, Storage Buckets support, or cross-browser proof.

## rev0188 linked work — 2026-07-08 — Lazy root / storage posture subpath / package budget refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0188 is linked work only.
- Substance: `src/public-api.mjs` now keeps the supported package-root export set while lazy-importing the full `src/browserrt.mjs` facade only inside `boot()`.
- Package surface: added typed `browserrt/browser-storage-posture` subpath; `browser-storage-posture.mjs` now exports the receipt format and admission-policy builder.
- Audit/refactor: public API and package boundary audits now gate the lazy root and typed subpath; installed-package smoke proves the subpath receipt and that the subpath does not expose `boot`.
- Budget: source blank-line compaction saved `1406` bytes; package src bytes are `1449367` / `1450000`, tarball file count is `73` / `75`.
- Non-claim: no publication, runtime promotion, root tarball slimming, quota reservation, eviction survival, fsync durability, Storage Buckets support, or cross-browser lifecycle proof.

## rev0187 linked work — 2026-07-08 — OPFS posture receipt / byte ledger / budget refactor

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0187 is linked work only.
- Substance: `diagnoseBrowserStoragePosture()` now returns `browserrt.browser-storage-posture-receipt.v1` with quota estimate, internal byte ledger, persistence status/request, Web Locks/Buckets availability, last mutation receipt, admission status, and quota/eviction/privacy non-claim proof flags.
- Runtime surface: postured OPFS factories now return `postureReceipt` directly and trace receipt/ledger presence.
- Audit/refactor: posture probe and contract audit prove both estimate-only and supplied-ledger receipt paths; runtime-core closure is `7` / `129297`; package src bytes are `1449999` / `1450000`.
- Non-claim: no publication, runtime promotion, quota reservation, eviction survival, fsync durability, Storage Buckets support, root-entry slimming, or cross-browser lifecycle proof.


## rev0186 linked work — 2026-07-08 — Mission heart / waste map / core-slim OPFS posture

- Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal; rev0186 is linked analysis only.
- Heart: boring browser-local mutation; correction: tiny default import plus visible OPFS posture receipt.
- Waste: proof-product inversion, root-entry weight, metadata split-brain risk, validation churn, mission diffusion. Metrics: root closure `40` / `1188216`; runtime-core `7` / `129186`.
- Non-claim: no publication, runtime promotion, Storage Buckets support, browser durability guarantee, cross-browser lifecycle proof, root-entry slimming, or browser-light lifecycle proof.

## rev0185 linked work — 2026-07-08 — Runtime-core blocked-dispatch reobserve/prune

- Current packaged head remains rev0125 / `0.0.125`; rev0185 added/pruned `blockedDispatches` so repeated foreign shared-scheduler stalls are counted without fossilizing. Runtime-core closure stayed `129186` bytes / `7` files under guard.
- Historical details remain in linked receipts, docs, and datacube-audit artifacts.
