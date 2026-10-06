# Cloudtainer deep read — rev0198 — mission/waste correction map

Current packaged head remains `rev0125` / `0.0.125` / OPFS Raw Composite AbortSignal. Linked `rev0198` is analysis and direction-setting only; it does not promote runtime, publish a package, or widen any durability claim.

## Heart of the mission

BrowserRT is not trying to be a browser OS. Its heart is a small browser-local mutation kernel for heavy local web apps: admit work before mutation, preserve caller/timeout/close cancellation through provider calls, coordinate same-origin OPFS with Web Locks where available, record receipts that make recovery honest, and keep quota/eviction/crash non-claims visible.

The useful product is the boring path: a web app can put a large local object, fail before unsafe mutation when the budget or lifecycle says no, recover or explain what happened, and avoid pretending that OPFS is durable cloud storage.

## What is missing

1. **Tiny default import.** The package root is lazy, but the product still ships a broad source surface. `runtime-core` is the closest honest seam; the next product move should make the tiny path first-class and leave demo/support machinery outside the default adoption path.
2. **Privacy and IO-abuse posture.** Current posture covers quota, estimates, persistence status, Web Locks, and write budgets. It does not yet treat OPFS itself as a measurable disk-timing and local free-space risk. Add a `byteTimeGuard` / `ioPrivacyBudget` before more high-IO OPFS proofs.
3. **Cross-browser decision table.** Managed Chromium is good evidence, not a browser matrix. Keep Chrome as the proving ground, but explicitly classify Firefox/Safari support/fallbacks before claiming local-first readiness.
4. **Storage Buckets posture, not guarantee.** Buckets can improve lifecycle/eviction organization where available, but support is not a general BrowserRT guarantee. Add capability detection and docs before implementation.
5. **Human-readable source posture.** `src/browser-storage-posture.mjs` has been compacted into a one-line source file to save budget. That is a smell: generated compact output belongs in a build/package step, not in the human-maintained source head.
6. **A user-value demo.** The cube proves many edge conditions. It still needs a tiny end-user story: import data, write local blocks, show storage posture, recover from close/timeout/quota, export/backup.

## What has gone severely wrong or wasteful

The severe waste is proof-product inversion. The cube is rich in receipts, tools, audits, and historical linked work, while the runtime surface remains small and cautious. The current extracted cube contains 1300 files. By top-level bytes before this note, `tools` is about 4,630,353 bytes, `src` about 1,449,265, `docs` about 824,289, and `artifacts` about 370,134. The existing artifact budget audit reported 8,345,811 total bytes against an 8,388,608-byte soft budget, with only 42,797 bytes of margin.

The package boundary is also too tight. The rev0197 receipt reports `srcBytes` 1449265 against a 1450000 limit, `fileCount` 73 / 75, and unpacked bytes 1683100 / 1800000. That is not just discipline; it is operating at the edge where useful changes start being shaped by budget gymnastics.

The good news is that the cube has been correcting this over time: historical docs were tombstoned, duplicate artifacts compacted, package boundary audits added, linked metadata consistency guarded, and package-time JSON compaction introduced. The next correction should be structural rather than another prose/audit layer.

## Online research read-through

- OPFS is origin-private and optimized for local file access, but it is still quota-bound and deleted when site data is cleared. BrowserRT's no-eviction/no-durability posture is correct.
- Storage quota/eviction remains browser-managed and `StorageManager.estimate()` is posture evidence, not reservation. BrowserRT should keep preflight admission conservative.
- Web Locks can abort queued requests, but the specification says a signal is ignored once the lock has been granted. Rev0197 correctly pushed close-composed cancellation into provider open/mutation paths after acquisition.
- Storage Buckets are a plausible future posture layer in Chromium-class browsers because they organize local data into buckets with durability/persistence policy. They should be treated as a capability branch, not a guarantee.
- FROST-style OPFS SSD timing research changes the risk model: high-volume OPFS IO is not merely quota/durability risk; it can also be privacy/side-channel surface. BrowserRT should make high-IO budgets explicit and user-visible.

## Change order

1. **Split the package:** publish/pack a tiny `runtime-core`/public wedge and move demo, support-bundle replay, and broad examples out of the default package files.
2. **Move evidence out of the active cube:** keep current receipts and indexes; archive historical verbose evidence outside the working cloudtainer.
3. **Add IO privacy budget:** cap planned OPFS bytes, operation rate, and temporary/staged amplification by session; record cleanup receipts; refuse silent oversized local files.
4. **Make storage posture a product surface:** expose a small receipt suitable for UI copy: status, estimated free budget, persistence state, Web Locks state, last cleanup, and non-claims.
5. **Add a minimal browser matrix:** one green Chromium proof, plus Firefox/Safari capability/fallback probes that classify unsupported/partial behavior without pretending conformance.
6. **Unminify human source:** restore readable `browser-storage-posture` source and, if necessary, produce compact package output during packaging.

## Non-claims

No runtime promotion, semver change, package publication, OPFS quota reservation, eviction survival, fsync/power-loss durability, browser-kill recovery, Web Lock fairness, Storage Buckets support, FROST mitigation, privacy guarantee, Service Worker lifetime, production readiness, or cross-browser proof.
