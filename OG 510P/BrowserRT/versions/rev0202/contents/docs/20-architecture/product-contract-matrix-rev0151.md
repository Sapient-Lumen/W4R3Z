# Product contract matrix — rev0151 linked risk cut

Runtime current office remains `rev0125` / `0.0.125` / OPFS Raw Composite AbortSignal. This linked matrix is not a runtime promotion. It exists to turn the mission into product promises that can be tested, supported, or explicitly rejected.

## Heart of the mission

BrowserRT should be a small, supportable browser-local failure kernel for heavy web apps. The product contract starts with admission before mutation and never turns `StorageManager.estimate()` into a persistent storage grant, quota reservation, or eviction survival claim. OPFS timing side-channel research is treated as a privacy/resource posture input, not as a product feature. The center is not “make a browser OS” and not “collect proofs forever.” The center is: before local work mutates browser storage, say whether the work was admitted; while it mutates, say who coordinated it; after failure, say what was actually mutated, what is safe to recover, what needs human review, and what remains outside the claim.

The current proof anchors remain `opfs:block-store-raw-composite-abort-signal-proof`, `browser:opfs-block-store-raw-composite-abort-signal-proof`, and `facility:opfs-block-store-raw-composite-abort-signal-contract-audit`. Continuity terms: opfsasyncblockstore, AbortSignal, signal, OPFS, Web Locks, browser-light.

## Matrix

| Product promise | Current evidence | Missing/risky seam | Next change |
| --- | --- | --- | --- |
| Admit before mutation | Storage posture and write-budget gates reject some work before OPFS mutation. | The public API still reads like a low-level storage toolkit instead of a user-facing admission contract. | Add a compact support-bundle field named `admissionDecision` with `accepted`, `rejectedBeforeMutation`, and `unknown` states. |
| Coordinate same-origin actors | WebLockGuardedBlockStore and Web Lock timeout proofs keep contention visible. | Web Locks cancellation has a spec boundary: abort before grant rejects with `AbortError`, but once granted the signal is ignored. | Keep provider-abort semantics separate from pending-lock abort and expose both in support bundles. |
| Preserve OPFS mutation truth | Raw composite AbortSignal proof verifies digest/prefix semantics after abort. | OPFS is origin-private and quota-bound; clearing site data deletes it, and `navigator.storage.estimate()` is only an estimate. | Add `storageEstimateAtAdmission` and `storageEstimateAtFailure` fields; never phrase them as quota reservation. |
| Recover only with proof | Provider-abort guidance and staged recovery tests require digest/prefix verification. | The operator loop still lacks one short recovery playbook mapped to support-bundle rows. | Add a recovery decision table: `retry`, `repair`, `exportForReview`, `discardCandidate`, `doNotRecoverYet`. |
| Stay browser-light unless browser evidence ran | Release remains browser-light while managed Chromium proofs are explicit browser tier. | First-read docs can accidentally imply cross-browser or lifecycle confidence. | Keep every first-read doc saying no cross-browser, quota, eviction, crash, or Service Worker lifecycle guarantee unless that evidence exists. |
| Bound artifact growth | rev0151 compacts inactive evidence, linked receipts, impact maps, surface inventory, and manifest prose. | Generated proof archives can grow until no one can finish the actual product. | Treat artifact-budget pass as a linked-turn gate; raw evidence must become compact receipts unless current-office central metadata requires it. |
| Acknowledge privacy/security posture | FROST shows OPFS can be used for SSD timing side-channel research. | High-I/O OPFS probes could become privacy-risky or wasteful if copied into product demos. | Add a “no hidden high-I/O fingerprinting probes” policy; demos must disclose large OPFS writes and keep byte budgets small. |
| Prepare future bucket routing | Storage Buckets can make eviction policy more predictable and bucket quotas are hints, not hard guarantees. | Browser support and semantics are still not the current claim. | Add a future adapter seam for bucket routing, guarded by feature detection and non-claim language. |
| Support SQLite/Wasm users honestly | SQLite wasm OPFS persistence can depend on SharedArrayBuffer and cross-origin isolation for some VFS paths. | BrowserRT should not promise third-party DB compatibility without COOP/COEP posture. | Add cross-origin-isolation checks only as diagnostics, not as a runtime requirement, until a real DB adapter exists. |
| Dogfood the support loop | Kernel Kit demos already create support-bundle evidence. | The demo path still risks being too much proof harness and not enough operator story. | Build one small “project workspace” dogfood that intentionally fails quota/admission/abort cases and shows the support bundle. |

## What has gone severely wrong or wasteful

The severe waste is not a broken proof; it is uncontrolled proof carrying. The cube accumulated repeated manifest prose, historical generated artifacts, linked-turn receipts, and registry-like surface files. That makes each turn more likely to spend time preserving bureaucracy instead of reducing user risk. The correction is not to delete truth. The correction is to keep current-office evidence and convert inactive or historical evidence into hash indexes and compact receipts.

The second risk is semantic overclaiming. OPFS and Web Locks are useful, but they do not give cross-browser durability, quota reservation, eviction survival, fsync/power-loss durability, crash recovery, Web Lock fairness, or Service Worker lifecycle confidence by default. The cube must keep these as non-claims until a specific proof promotes one.

The third risk is privacy and resource posture. Browser APIs that permit large local storage can support powerful apps, but recent OPFS timing research shows local storage timing can be a side-channel. BrowserRT should not normalize hidden high-I/O probes, large background OPFS files, or demo flows that look like fingerprinting.

## Research notes used by this linked pass

- MDN OPFS: `https://developer.mozilla.org/en-US/docs/Web/API/File_System_API/Origin_private_file_system`
- W3C Web Locks: `https://www.w3.org/TR/web-locks/`
- Chrome Storage Buckets: `https://developer.chrome.com/docs/web-platform/storage-buckets`
- WICG Storage Buckets explainer: `https://github.com/WICG/storage-buckets/blob/main/explainer.md`
- FROST OPFS SSD timing paper: `https://hannesweissteiner.com/pdfs/frost.pdf`
- FROST publication page: `https://tugraz.elsevierpure.com/en/publications/frost-fingerprinting-remotely-using-opfs-based-ssd-timing/`
- SQLite wasm OPFS persistence: `https://sqlite.org/wasm/doc/trunk/persistence.md`
- MDN SharedArrayBuffer: `https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer`
- web.dev cross-origin isolation guide: `https://web.dev/articles/cross-origin-isolation-guide`

## Stop doing

Stop adding registry rows unless they map to a product promise in this matrix. Stop keeping generated artifacts in the hot package when a hash-indexed receipt preserves enough truth. Stop adding browser-heavy probes to release. Stop treating `AbortSignal` as one generic cancellation story; pending-lock abort and post-grant provider abort are different. Stop implying persistent-storage grants, quota reservation, eviction survival, general crash recovery, or cross-browser behavior without proof.
