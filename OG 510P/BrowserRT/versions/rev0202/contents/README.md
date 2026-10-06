# BrowserRT rev0125 / linked rev0202

Current packaged head: `rev0125` / `0.0.125` / OPFS Raw Composite AbortSignal. Linked rev0202 is a runtime-core recovery-guidance table refactor and closure ratchet, not a runtime promotion.

Read first: `docs/00-meta/cloudtainer-forward-momentum-rev0202-2026-07-08-runtime-core-recovery-guidance-table-ratchet.md`, `artifacts/datacube-audit/REV0125-RUNTIME-CORE-RECOVERY-GUIDANCE-TABLE-RATCHET-REV0202.json`, `artifacts/research/REV0125-BROWSER-RUNTIME-SOURCE-CHECK-REV0202.json`, `REV0202-LINKED-REVISION-RECEIPT.json`.

Substance: browser storage recovery guidance now uses compact code-classification and recovery-step tables instead of repeated switch/if branches. The public recovery guidance shape remains covered by the storage posture probe, while the runtime-core audit ratchets the closure limit from 130,000 to 128,500 bytes.

Observed seam: rev0201 runtime-core was 129,576 / 130,000 bytes. Rev0202 is 128,028 / 128,500 bytes across 6 files, with `src/product-wedge.mjs` still absent. Package `src` is 1,393,791 / 1,450,000 bytes and the explicit public/runtime source allowlist remains green.

Carry-forward anchors: `browser:opfs-block-store-raw-composite-abort-signal-proof`, `facility:runtime-core-entry-contract-audit`, `facility:package-tarball-boundary-contract-audit`, opfsasyncblockstore, OPFS, Web Locks, abortSignal, signal, composite, browser-light.

Non-claims: no production runtime, package publication, root facade split, quota reservation, eviction survival, fsync/power-loss durability, Storage Buckets support, Web Lock fairness, Service Worker lifetime, browser-kill or crash recovery, privacy guarantee, browser-light release coverage, or cross-browser proof.
