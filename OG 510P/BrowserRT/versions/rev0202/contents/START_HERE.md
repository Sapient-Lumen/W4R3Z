# Start here — BrowserRT rev0202

Current packaged head: `rev0125` / `0.0.125`; current office remains rev0125. Linked rev0202 is a runtime-core recovery-guidance table refactor, not a runtime promotion.

Read first: `docs/00-meta/cloudtainer-forward-momentum-rev0202-2026-07-08-runtime-core-recovery-guidance-table-ratchet.md`, `artifacts/datacube-audit/REV0125-RUNTIME-CORE-RECOVERY-GUIDANCE-TABLE-RATCHET-REV0202.json`, `artifacts/research/REV0125-BROWSER-RUNTIME-SOURCE-CHECK-REV0202.json`, `REV0202-LINKED-REVISION-RECEIPT.json`.

Risk selected: runtime-core was too close to its closure cliff after storage posture work. The correction converts recovery guidance branching into compact table data, preserves storage/recovery proof coverage, and tightens the runtime-core closure ratchet instead of adding another registry or widening limits.

Current result: runtime-core closure is 128,028 / 128,500 bytes across 6 files; package source is 1,393,791 / 1,450,000 bytes; package examples remain 218,374 / 220,000 bytes.

Carry-forward anchors: `facility:opfs-block-store-raw-composite-abort-signal-contract-audit`, `facility:runtime-core-entry-contract-audit`, `facility:package-tarball-boundary-contract-audit`, opfsasyncblockstore, OPFS, Web Locks, abortSignal, signal, composite, browser-light.

Non-claims: no runtime promotion, publication, production readiness, root facade split, quota reservation, eviction survival, fsync durability, Storage Buckets support, Web Lock fairness, Service Worker lifetime, browser-kill or crash recovery, privacy guarantee, or cross-browser guarantee.

Current proof string retained for audits: `browser:opfs-block-store-raw-composite-abort-signal-proof`. Current audit: `facility:opfs-block-store-raw-composite-abort-signal-contract-audit`. Runtime spelling anchors: opfsasyncblockstore, abortSignal, signal, browser-light.
