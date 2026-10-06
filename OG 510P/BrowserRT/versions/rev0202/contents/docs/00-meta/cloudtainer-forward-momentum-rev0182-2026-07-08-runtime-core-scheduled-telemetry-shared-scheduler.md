# rev0182 forward momentum — runtime-core scheduled telemetry / shared scheduler

Current packaged head remains `rev0125` / `0.0.125` / OPFS Raw Composite AbortSignal. `rev0182` is linked cloudtainer hardening only; it is not a runtime promotion, semver change, package publication, OPFS durability claim, or cross-browser guarantee.

Risk addressed: the slim `browserrt/runtime-core` adapter listed `estimate`, `snapshot`, and `cleanup` as lane ops but did not expose scheduled methods or `submit()` parity, forcing adoption users to inspect/clean the memory store out-of-band. A second audit seam was shared-scheduler safety: `dispatchOne()` could consume the scheduler's next task even when that task was not adapter-owned.

Changes:
- Added light adapter `scheduleEstimate()`, `scheduleSnapshot()`, `scheduleCleanupForTest()`, and `submit()` parity.
- Added `CrossLaneScheduler.dispatchNext({ flowId, metadataComponent })` filtering and changed the runtime-core adapter to dispatch only its own storage work.
- Added typed runtime-core declaration interfaces for the memory store, scheduler, and light lane adapter.
- Extended source and installed package probes to prove scheduled telemetry/cleanup and preservation of a foreign critical task in a shared scheduler.

Measured proof: runtime-core static closure is `122741` bytes / `7` files under the 125 KB / 7 file ratchet. Installed package smoke passed with 72 files, 1674866 unpacked bytes, 794-byte installed package.json, `telemetryCleanupScheduled: true`, and `sharedSchedulerForeignPreserved: true`.

Research applied: browser storage quota/usage remains estimate-based and eviction-managed; abortable and scheduled work should remain cancelable while pending. Therefore the next risky work should keep storage pressure and queue ownership explicit instead of hiding work behind optimistic queues.

Next risk: move visible OPFS byte/time/privacy posture into the browser demo/adoption path before high-I/O mutation starts, while preserving the runtime-core closure ratchet.
