## rev0054 — 2026-06-01

### Kernel Kit Readiness Contrast Workbench

- Added `src/kernel-kit-readiness-contrast.mjs` with `createKernelKitReadinessContrast()`, `createDegradedKernelKitReadinessGate()`, and `validateKernelKitReadinessContrast()`.
- Added release-tier proof `demo:kernel-kit-readiness-contrast-proof` and audit `facility:kernel-kit-readiness-contrast-audit`.
- Extended the demo page with a **Show degraded readiness contrast** control and output panel.
- Extended the explicit browser Kernel Kit proof so CDP drives `window.BrowserRTKernelKitDemo.buildReadinessContrast()` through the same page API a human uses.
- Audited/refactored runtime exports, type declarations, manifest, impact map, surface inventory, handoff docs, receipt metadata, and non-claim surfaces around the contrast workbench.

### Non-claims

No production readiness-contrast claim. No automated regression detection claim. No automated demo-go/no-go claim. No product-market-fit claim. No production runtime claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. Broad release remains browser-light.

## rev0053 — 2026-05-31

### Kernel Kit Readiness Gate Workbench

- Added `src/kernel-kit-readiness-gate.mjs` with `createKernelKitReadinessGate()` and `validateKernelKitReadinessGate()`.
- Added release-tier proof `demo:kernel-kit-readiness-gate-proof` and audit `facility:kernel-kit-readiness-gate-audit`.
- Extended the demo page with a **Build readiness gate** control and output panel.
- Extended the explicit browser Kernel Kit proof so CDP drives `window.BrowserRTKernelKitDemo.buildReadinessGate()` through the same page API a human uses.
- Audited/refactored runtime exports, type declarations, manifest, impact map, surface inventory, handoff docs, receipt metadata, and non-claim surfaces around the readiness gate.

### Non-claims

No production readiness-gate claim. No automated demo-go/no-go claim. No product-market-fit claim. No production runtime claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. Broad release remains browser-light.

## rev0052 — 2026-05-31

### Kernel Kit Handoff Markdown Import Workbench

- Added `src/kernel-kit-handoff-reader.mjs` with `createKernelKitHandoffMarkdownImportReport()` and `validateKernelKitHandoffMarkdownImportReport()`.
- Added release-tier proof `demo:kernel-kit-handoff-markdown-import-proof` and audit `facility:kernel-kit-handoff-markdown-import-audit`.
- Extended the demo page with a **Validate handoff Markdown** control, import textarea, and import report output.
- Extended the explicit browser Kernel Kit proof so CDP drives `window.BrowserRTKernelKitDemo.importHandoffMarkdown()` through the same page API a human uses.
- Audited/refactored runtime exports, type declarations, manifest, impact map, surface inventory, handoff docs, receipt metadata, and non-claim surfaces around the new import loop.

### Non-claims

No production handoff-markdown import claim. No automated next-session correctness claim. No support-bundle authenticity or signature claim. No telemetry backend ingestion claim. No production runtime claim. Broad release remains browser-light.

## rev0051 — 2026-05-31

### Kernel Kit Handoff Markdown Workbench

- Added `src/kernel-kit-handoff-markdown.mjs` with handoff Markdown generation and validation.
- Added release-tier proof `demo:kernel-kit-handoff-markdown-proof` and audit `facility:kernel-kit-handoff-markdown-audit`.
- Extended the explicit browser Kernel Kit proof so CDP verifies handoff Markdown creation through the page API.
- Preserved support bundle, support-bundle import, support-bundle diff, guided tour, and browser-light release posture.

### Non-claims

No production handoff-markdown claim. No automated next-session correctness claim. No support-bundle authenticity or signature claim. No production runtime claim.

## rev0047 — 2026-05-30

### Kernel Kit Diagnostic Runbook

- Added diagnostic runbook helpers: `createKernelKitDiagnosticRunbook()` and `validateKernelKitDiagnosticRunbook()`.
- Added release-tier proof `demo:kernel-kit-diagnostic-runbook-proof` and audit `facility:kernel-kit-diagnostic-runbook-audit`.
- Updated the human page with `window.BrowserRTKernelKitDemo.diagnoseTraceComparison()` and a diagnostic runbook panel.
- Extended the explicit browser Kernel Kit proof so CDP drives run, reload, export, controlled failure, trace comparison, and diagnostic runbook through the same page API a human uses.
- Refactored future-session handoff docs so the diagnostic runbook says what changed, what stayed bounded, and exact next commands to run.
- Preserved broad release as browser-light.

Important non-claims: no production runtime claim, no production observability claim, no root-cause analysis claim, no automated failure recovery claim, no production incident-response claim, no OPFS durability/quota/eviction/crash-recovery/browser-restart claim, no cross-browser claim, no WebGPU/performance claim, no exactly-once delivery claim.

## rev0044 — 2026-05-30

### Kernel Kit Trace Handoff Workbench

- Added the Kernel Kit trace/export workbench: `createKernelKitTraceExport()`, browserrt-json receipt export, Chrome-trace-shaped JSON export, and explicit non-claims around production observability and Chrome DevTools/Perfetto compatibility.
- Added release-tier proof `demo:kernel-kit-trace-export-proof` and audit `facility:kernel-kit-trace-export-audit`.
- Added `src/kernel-kit-demo-usefulness.mjs` with `createKernelKitDemoUsefulnessReport()` and `validateKernelKitDemoUsefulnessReport()`.
- Added release-tier proof `demo:kernel-kit-usefulness-proof` and audit `facility:kernel-kit-usefulness-audit`.
- Added a local reload handoff for the human page: the demo stores an OPFS ref/digest handoff in localStorage, `reloadRead()` can verify after page reload without hidden probe args, then clears the handoff after successful readback.
- Added release-tier audit `facility:kernel-kit-handoff-contract-audit` and strengthened the explicit browser proof so CDP uses the same page-level handoff a human would use.
- Updated the human demo page to render the observatory, trace/export receipt, usefulness scorecard, reload handoff status, and non-claim boundaries.
- Preserved `browser:kernel-kit-demo-proof` as explicit browser/full tier and kept broad release browser-light.

Important non-claims: no user research claim, no adoption evidence claim, no pricing/market-size/product-market-fit claim, no production runtime claim, no production observability claim, no Chrome DevTools/Perfetto compatibility claim, no local reload handoff durability or crash-recovery claim, no OPFS durability/quota/eviction/crash-recovery/browser-restart claim, no cross-browser claim, no WebGPU/performance claim.

## rev0043 — 2026-05-30

### Kernel Kit Page Runner

- Moved the browser Kernel Kit demo flow into `demo/kernel-kit-demo-runner.mjs`, exposing `window.BrowserRTKernelKitDemo.run()`, `reloadRead()`, and `render()`.
- Updated `demo/kernel-kit-demo.html` from a placeholder into a human-clickable page with run button, rendered stage transcript, proof summary, non-claims, and JSON artifact.
- Refactored `tools/browser_kernel_kit_demo_probe.mjs` so CDP drives the same page API a human can call instead of embedding the demo logic in the probe.
- Added transcript helpers to `src/kernel-kit-demo.mjs` and exported them through BrowserRT/types.
- Added release-tier page contract audit `facility:kernel-kit-page-contract-audit`.
- Preserved `browser:kernel-kit-demo-proof` as explicit browser/full tier and kept broad release browser-light.

Important non-claims: no production runtime claim, no UX validation claim, no user-demand proof, no market/product-fit claim, no OPFS durability/quota/eviction/crash-recovery/browser-restart claim, no WebGPU/cross-browser/performance claim, no exactly-once delivery claim.

## rev0042 — 2026-05-30

Codename: Integrated Kernel Kit Demo.

- Added the first integrated BrowserRT Kernel Kit usefulness proof: runtime boot, browser Worker agent, transfer object ref, watermark admission governor, OPFS storage-lane adapter, validation, and trace report.
- Added `src/kernel-kit-demo.mjs` with `createKernelKitDemoPlan()` and `validateKernelKitDemoReport()`.
- Added explicit browser slice `browser:kernel-kit-demo-proof`.
- Added release-tier audit `facility:kernel-kit-demo-audit`.
- Added human-facing `demo/kernel-kit-demo.html`.
- Updated future-session handoff docs so the integrated demo is legible as a usefulness wedge, not a production or market claim.
- Preserved broad release as browser-light.

Important non-claims: no production runtime claim, no market validation claim, no OPFS durability/quota/eviction/crash-recovery/browser-restart claim, no OPFS sync access handle proof in the integrated demo, no browser Worker OPFS storage-lane proof in the integrated demo, no WebGPU proof, no cross-browser conformance claim, no throughput/latency performance claim.

## rev0041 — 2026-05-30

Codename: Continue Narrow Wedge.

- Added a mile-high go/no-go assessment: continue BrowserRT, but narrow the first useful wedge and keep moonshot claims evidence-gated.
- Added project-worth and beneficiary docs separating who needs BrowserRT, who does not, and what would prove demand.
- Added `src/project-assessment.mjs` with `createProjectContinuationAssessment()` and `validateProjectContinuationAssessment()`.
- Added release-tier audit `facility:project-worth-audit` so future sessions can verify the decision surface, docs, research registry, and non-claim posture without launching Chromium.
- Added related-work pass 036 around WebContainers, Comlink, workerd, Deno permissions, DuckDB-Wasm, SQLite-Wasm/OPFS, Tauri, Ray object refs, OPFS, SAB, WebGPU, and Web Locks.
- Preserved broad release as browser-light and preserved OPFS/WebGPU/WebNN/WebTransport/WebRTC/mobile/security/performance non-claims.

Important non-claims: no market validation claim, no user-demand proof, no product-market-fit claim, no production runtime claim, no WebGPU performance claim, no OPFS durability/quota/eviction/crash-recovery claim, no cross-browser conformance claim.

## rev0040 — 2026-05-30

Codename: Mile High Dream Boundary.

- Switched gears to a mile-high vision pass: BrowserRT as one browser userspace kernel with many capability-gated providers.
- Added `src/dream-boundary.mjs` with `createDreamBoundaryMap()` and `validateDreamBoundaryMap()`.
- Added release-tier audit `facility:mile-high-boundary-audit`.
- Added cloudtainer testability shelf docs separating cloudtainer-buildable, smoke-testable, needs-external-evidence, and shelf-until-repeated-container-evidence surfaces.
- Added new related-work/dreambank pass covering WebContainers, workerd/Workers, Deno/WinterTC, Ray, Temporal, Durable Objects, Tauri, WASI, the WebAssembly Component Model, WebGPU, WebNN, WebTransport, WebRTC, OPFS, SharedArrayBuffer, and Web Locks.
- Preserved broad release as browser-light and added explicit WebGPU/WebNN/WebTransport/WebRTC/mobile/security/performance non-claims.

Important non-claims: no new runtime provider behavior proof in rev0040, no WebGPU performance claim, no WebNN/NPU claim, no real WebTransport/WebRTC WAN/NAT claim, no mobile/background lifecycle claim, no production security sandbox claim, no OPFS durability or quota/eviction/crash-recovery claim, no cross-browser conformance claim.

## rev0039 — 2026-05-30

Codename: OPFS Storage Lane Adapter.

- Added `OpfsBlockStoreStorageLaneAdapter` as a narrow browser-window async OPFS block-store storage-lane bridge.
- Added explicit browser slice `browser:opfs-storage-lane-adapter-proof`.
- Added release-tier audit `facility:opfs-storage-lane-adapter-contract-audit`.
- Refactored the adapter path onto `BlockStoreLaneAdapter` + `StorageLaneExecutor` so the source, proof, and docs agree.
- Preserved browser-light broad release and OPFS durability/quota/crash-recovery/sync-handle/multi-tab/performance non-claims.

## rev0038 — 2026-05-30

Codename: OPFS Block Store Bridge.

- Added `OpfsAsyncBlockStore` as a browser-window async OPFS content-addressed block-store provider.
- Added `browser:opfs-block-store-proof`, an explicit browser/full-tier Chromium/CDP proof for put/get/has/verify/delete, duplicate dedupe, page-reload readback in one temporary profile, storage estimate, cleanup, trace evidence, and policy restoration.
- Added `facility:opfs-provider-contract-audit`, a release-tier non-browser audit for provider source/export/type/doc/manifest/research/proof/non-claim coherence.
- Added related-work/dreambank pass 033 around OPFS provider variants, SQLite Wasm OPFS VFS tradeoffs, storage quotas/eviction, and async-vs-sync OPFS boundaries.
- Refactored docs and handoff surfaces so future sessions do not mistake page-reload readback for durability, crash recovery, quota behavior, multi-tab coordination, or cross-browser conformance.
- Preserved broad release as browser-light.

Important non-claims: no OPFS durability/fsync/quota/eviction/crash-recovery/browser-restart claim, no OPFS storage-lane provider integration proof, no OPFS sync access handle block-store proof, no OPFS performance claim, no cross-browser/WebGPU claim.

## rev0037 — 2026-05-30

Codename: Storage Lane Overload Governance Model.

- Added `StorageLaneOverloadGovernanceModelOracle`.
- Added `scheduler:storage-lane-overload-governance-model-proof`.
- Added `facility:storage-lane-overload-governance-contract-audit`.
- Added rev0037 research/dreambank docs for overload-governance histories.
- Cohered future-session handoff and non-claim surfaces around fake-provider overload-governance before OPFS/browser spending.
- Refactored the release tier so carried-forward semantic proof tasks remain release-visible while older per-rung contract audits move to audit/full; the current overload-governance contract audit stays release-tier.
- Fixed a packaging-manifest race by snapshotting file bytes once before writing the zip, preventing late-settling proof artifacts from skewing `RELEASE-MANIFEST.json` hashes.

## rev0036 — 2026-05-29

Codename: Storage Lane Admission Model Oracle

- Added `StorageLaneAdmissionHistoryModelOracle` and `compareStorageLaneAdmissionHistoryToModel`.
- Added `scheduler:storage-lane-admission-model-proof`, a release-tier generated-history/model oracle for storage-lane admission behavior.
- Added `facility:storage-lane-admission-model-contract-audit` to keep source/runtime/docs/manifest/impact/inventory/research/proof/non-claims coherent.
- Added related-work/dreambank pass 031 around model-based testing, Reactive Streams backpressure, Kubernetes API Priority and Fairness, and Google SRE retry/load-shedding pressure.
- Audited/refactored current handoff surfaces so future sessions see rev0036's fake-provider model claim separately from rev0035's targeted admission-history proof.
- Preserved broad release as browser-light.

Non-claims: no OPFS/browser Worker storage-lane admission-history model proof, no production overload-governance claim, no exhaustive formal verification/model checking claim, no performance/durability/exactly-once/cross-browser/WebGPU claim.

## rev0035 — 2026-05-29

Codename: Storage Lane Admission History.

- Added `StorageLaneAdmissionHistoryRunner` as a fake-provider composition surface wrapping `ProviderResilienceHistoryRunner` with `WatermarkAdmissionController`.
- Added concrete slice `scheduler:storage-lane-admission-history-proof`, proving admission success, transient retry under admission, watermark rejection/no-mutation, critical bypass, provider-health rejection/recovery, hard-limit rejection/no-mutation, and final empty lease accounting.
- Added audit slice `facility:storage-lane-admission-history-contract-audit`.
- Added related-work/dreambank pass 030 around overload managers, priority/fairness, backpressure, and bulkhead isolation as admission-control design pressure.
- Refactored currentness/handoff surfaces so future sessions see admission-history boundaries without losing provider-resilience model non-claims.
- Preserved broad release browser-light posture and fake-provider-first sequencing.

Important non-claims: no OPFS/browser storage-lane admission-history proof, no production overload-governance or admission-control claim, no wall-clock/performance/SLO/durability/exactly-once/cross-browser/WebGPU claim, no formal verification claim.

## rev0034 — 2026-05-29

Codename: Provider Resilience Model Oracle.

- Added `ProviderResilienceModelOracle` as an independent fake-provider model for composed provider-resilience histories.
- Added concrete slice `scheduler:provider-resilience-model-proof`, comparing `ProviderResilienceHistoryRunner` against the model over 22 targeted/generated scenarios and 124 operations.
- Added audit slice `facility:provider-resilience-model-contract-audit`.
- Added related-work/dreambank pass 029 around history checking, deterministic simulation, model oracles, and resilience state machines.
- Fixed a real retry-budget lease-accounting bug: operation-level `maxAttempts` now wins before another retry lease can be acquired.
- Preserved broad release browser-light posture and fake-provider-first sequencing.

Important non-claims: no OPFS/browser provider-resilience model proof, no true concurrent history proof, no production resilience or retry-storm safety claim, no wall-clock/performance/SLO/durability/exactly-once/cross-browser/WebGPU claim, no formal verification claim.

## rev0033 — 2026-05-29

Codename: Provider Resilience History Office.

- Added `ProviderResilienceHistoryRunner` as a fake-provider composition surface for storage-lane scheduling, persisted-spill enqueue, retry policy, retry-budget admission, and circuit-breaker/bulkhead gates.
- Added concrete slice `scheduler:provider-resilience-history-proof`.
- Added audit slice `facility:provider-resilience-history-contract-audit`.
- Added related-work/dreambank pass 028 around resilience composition, retry budgets, circuit breaking, cascading-failure retry amplification, and deterministic provider histories.
- Cohered current handoff docs and non-claims so future sessions see the OPFS/browser/production/performance boundaries clearly.
- Preserved broad release browser-light posture.

Important non-claims: no OPFS/browser provider-resilience proof, no production resilience or retry-storm safety claim, no wall-clock/performance/SLO/durability/cross-browser/WebGPU claim, no formal verification claim.

## rev0032 — 2026-05-28

Codename: Circuit Breaker Model Oracle.

- Added `scheduler:circuit-breaker-bulkhead-model-proof`, a deterministic generated-history oracle for `CircuitBreakerBulkheadController`.
- Added `facility:circuit-breaker-bulkhead-model-contract-audit`.
- Added related-work/dreambank pass 027 around resilience pipelines, circuit breakers, bulkheads, resource limits, and model-based testing.
- Cohered current handoff docs and non-claims so future sessions see fake-provider/model boundaries clearly.
- Preserved broad release browser-light posture.

Important non-claims: no OPFS/browser circuit-breaker or bulkhead model proof, no production resilience claim, no exhaustive model checking or formal verification claim, no wall-clock/performance/SLO/durability/cross-browser/WebGPU claim.

## rev0031 — 2026-05-26

Codename: Circuit Breaker Bulkhead Office.

- Added `CircuitBreakerBulkheadController` as a fake-provider/virtual-tick resilience primitive.
- Added `scheduler:circuit-breaker-bulkhead-proof` covering bulkhead rejection, closed/open/half-open transitions, failure/slow thresholds, and trace evidence.
- Added `facility:circuit-breaker-bulkhead-contract-audit`.
- Refactored Makefile currentness so convenience targets derive current revision prefixes instead of carrying stale rev0029 paths.
- Preserved browser-light release posture and non-claims around OPFS/browser/production resilience.

## rev0030 — 2026-05-26

Codename: Retry Budget Model Oracle.

- Added `validateRetryBudgetAdmissionSnapshot` as a reusable invariant surface for retry-budget state.
- Added concrete slice `scheduler:storage-lane-retry-budget-model-proof`.
- Added audit slice `facility:storage-lane-retry-budget-model-contract-audit`.
- Added 32 deterministic retry-budget scenarios and 3,072 generated operations comparing `RetryBudgetAdmissionController` against a reference model.
- Added related-work/dreambank pass 025 around retry budgets, deterministic simulation, model-based testing, Jepsen-style history checking, and finite-model humility.
- Cohered future-session docs so the model proof is not mistaken for OPFS/browser behavior, production retry-storm safety, or formal verification.
- Broad release remains browser-light.

Important non-claims: no OPFS retry-budget model proof, no browser Worker retry-budget model proof, no production retry-storm safety claim, no exhaustive model checking or formal verification claim, no wall-clock/performance/SLO claim, no durability/eviction/exactly-once claim, no cross-browser claim.

## rev0029 — 2026-05-26

Codename: Retry Budget Admission Office.

- Added `RetryBudgetAdmissionController` as a fake-provider overload gate for storage-lane retries.
- Integrated `StorageLaneRetryController` with optional `retryBudget` admission before delayed retries schedule another attempt.
- Added concrete slice `scheduler:storage-lane-retry-budget-proof`.
- Added audit slice `facility:storage-lane-retry-budget-contract-audit`.
- Added related-work/dreambank pass 024 around retry budgets, circuit breaking, SRE overload, Envoy retry budgets, Kubernetes APF, and Resilience4j-style policy composition.
- Cohered future-session handoff docs and non-claims so retry-budget proof is not mistaken for OPFS/browser or production retry-storm safety.
- Broad release remains browser-light.

Important non-claims: no OPFS storage-lane retry-budget proof, no browser Worker storage-lane retry-budget proof, no retry-storm safety or production overload-governance claim, no wall-clock/performance/SLO claim, no durability/eviction/exactly-once claim, no cross-browser claim.

## rev0028 — 2026-05-26

Codename: Storage Lane Retry Oracle.

This revision keeps the storage-lane model oracle surfaces and adds a bounded fake-provider retry policy proof. The key move is to make retries a named runtime contract before spending OPFS/browser budget: logical operation id, attempt id, virtual backoff ticks, retryable/non-retryable codes, explicit provider-health recovery, and trace evidence.

Added:

- `src/storage-lane-retry.mjs` with `StorageLaneRetryPolicy` and `StorageLaneRetryController`.
- `tools/storage_lane_retry_policy_probe.mjs`.
- `tools/storage_lane_retry_contract_audit.mjs`.
- Manifest task `scheduler:storage-lane-retry-policy-proof`.
- Manifest task `facility:storage-lane-retry-contract-audit`.
- Artifact `artifacts/validation/REV0035-STORAGE-LANE-RETRY-POLICY-PROBE.json`.
- Artifact `artifacts/audit/REV0035-STORAGE-LANE-RETRY-CONTRACT-AUDIT.json`.
- `docs/05-research/related-work-research-pass-023.md`.
- `docs/20-architecture/runtime-dreambank-023.md`.
- `docs/20-architecture/storage-lane-retry-policy-frontier.md`.
- `docs/40-validation/storage-lane-retry-policy-slice.md`.
- `docs/40-validation/storage-lane-retry-contract-audit-rev0028.md`.
- `docs/00-meta/cube-audit-rev0028.md`.

Changed/factored:

- `src/browserrt.mjs`, `src/ipc.mjs`, and `src/types.d.ts` now expose the retry policy/controller surface.
- `test/smoke.mjs` now checks the runtime retry-controller factory and boot proof flag.
- The future-session office manual and non-claims charter carry a dedicated Rev0028 retry amendment.
- A duplicated non-claim sentence in `src/storage-lane-scheduler.mjs` was cleaned up.
- Broad release remains browser-light.

Earned:

- Transient fake-provider storage failure schedules a delayed retry without mutating provider/mailbox state on the failed attempt.
- Explicit provider-health recovery gates the successful retry attempt.
- Non-retryable storage errors fail finally without retry.
- Max-attempt exhaustion stops retry loops.
- Retry trace evidence spans retry controller, storage lane, scheduler, mailbox, and fake block provider.
- Storage-lane model-walk evidence remains available as a current release slice.

Non-claims: no OPFS storage-lane retry proof; no browser Worker storage-lane retry proof; no durability, fsync, quota, eviction, or crash-recovery claim; no exactly-once delivery claim; no retry-storm safety or production retry algorithm claim; no wall-clock timer, throughput, latency, SLO, WebGPU, or cross-browser conformance claim.

## rev0027 — 2026-05-26

Codename: Storage Lane Provider Integration.

This revision integrates the cross-lane scheduler with a fake persisted-spill mailbox provider through a canonical `StorageLaneExecutor`, then audits the new storage-lane/provider boundary.

Added:

- `src/storage-lane-scheduler.mjs` as the canonical storage-lane executor surface.
- `tools/storage_lane_provider_probe.mjs`.
- `tools/provider_integration_contract_audit.mjs`.
- Manifest task `scheduler:storage-lane-provider-proof`.
- Manifest task `facility:provider-integration-contract-audit`.
- Artifact `artifacts/validation/REV0035-STORAGE-LANE-PROVIDER-PROBE.json`.
- Artifact `artifacts/audit/REV0035-PROVIDER-INTEGRATION-CONTRACT-AUDIT.json`.
- `docs/05-research/related-work-research-pass-022.md`.
- `docs/20-architecture/runtime-dreambank-022.md`.
- `docs/20-architecture/storage-lane-provider-integration-frontier.md`.
- `docs/40-validation/storage-lane-provider-slice.md`.
- `docs/40-validation/provider-integration-contract-audit-rev0027.md`.
- `docs/00-meta/cube-audit-rev0027.md`.

Changed/factored:

- Runtime boot reports now expose `storageLaneProviderProof` and `storageLaneExecutor`.
- `src/browserrt.mjs`, `src/ipc.mjs`, and `src/types.d.ts` now expose the canonical storage-lane executor surface.
- Duplicate experimental storage-lane provider/coordinator surfaces were removed to avoid future-session ambiguity.
- Broad release remains browser-light.

Earned:

- Fake-provider `CrossLaneScheduler` can drive `PersistedSpillMailbox` operations through `StorageLaneExecutor`.
- The proof covers lane health rejection, capacity blocking, enqueue/dequeue/ack/checkpoint/snapshot, maintenance-lane compaction, dependency deferral, and live-ref-safe compaction.
- Trace evidence now spans scheduler, storage lane, mailbox, and fake block provider.

Non-claims: no OPFS storage-lane provider proof; no browser Worker storage-lane provider proof; no fsync, flush, quota, eviction, or durability claim; no production storage scheduler claim; no work stealing, deadlines, preemption, priority inheritance, fairness-SLO, throughput, latency, WebGPU, or cross-browser conformance claim.

## rev0026 — 2026-05-25

Codename: Persisted Spill Compaction.

This revision deepens the persisted-spill lane by adding fake-provider retained-ref compaction and a retention-contract audit/factor pass.

Added:

- `PersistedSpillMailbox.compact()`.
- `tools/persisted_spill_compaction_probe.mjs`.
- `tools/retention_contract_audit.mjs`.
- Manifest task `ipc:persisted-spill-compaction-proof`.
- Manifest task `facility:retention-contract-audit`.
- Artifact `artifacts/validation/REV0035-PERSISTED-SPILL-COMPACTION-PROBE.json`.
- Artifact `artifacts/audit/REV0035-RETENTION-CONTRACT-AUDIT.json`.
- `docs/05-research/related-work-research-pass-021.md`.
- `docs/20-architecture/runtime-dreambank-021.md`.
- `docs/20-architecture/persisted-spill-retention-compaction-frontier.md`.
- `docs/40-validation/persisted-spill-compaction-slice.md`.
- `docs/40-validation/retention-contract-audit-rev0026.md`.
- `docs/00-meta/cube-audit-rev0026.md`.

Changed/factored:

- `PersistedSpillMailbox` now tracks retained refs and live ready/pending refs separately.
- Checkpoints include retained refs.
- Compaction writes `compact-delete` journal records.
- Recovery replays `compact-delete` records.
- Current office surfaces now describe the rev0026 retained-ref compaction stair while preserving scheduler and recovery non-claims.
- Broad release remains browser-light.

Earned:

- Fake-provider retained-ref compaction can dry-run candidates without mutation.
- Live ready/pending content-addressed refs are protected, including duplicate payload digests shared by acked and live entries.
- Unreferenced retained blocks are deleted in the scripted proof.
- Compact-delete records replay during recovery.
- Pending entries redeliver at-least-once after recovery.

Non-claims: no OPFS persisted-spill proof; no browser Worker persisted-spill proof; no fsync, flush, quota, eviction, or durability claim; no production retention, compaction, or garbage-collection algorithm claim; no exactly-once delivery claim; no throughput, latency, real performance, WebGPU, or cross-browser conformance claim.

## rev0025 — 2026-05-25

Codename: Cross Lane Model Oracle.

This revision deepens the scheduler lane after rev0024 by adding a deterministic model-walk oracle and a scheduler-model audit/factor pass.

Added:

- `tools/cross_lane_model_walk_probe.mjs`.
- `tools/scheduler_model_contract_audit.mjs`.
- Manifest task `scheduler:cross-lane-model-walk-proof`.
- Manifest task `facility:scheduler-model-contract-audit`.
- Artifact `artifacts/validation/REV0035-CROSS-LANE-MODEL-WALK-PROBE.json`.
- Artifact `artifacts/audit/REV0035-SCHEDULER-MODEL-CONTRACT-AUDIT.json`.
- `docs/05-research/related-work-research-pass-020.md`.
- `docs/20-architecture/runtime-dreambank-020.md`.
- `docs/20-architecture/cross-lane-scheduler-model-frontier.md`.
- `docs/40-validation/cross-lane-model-walk-slice.md`.
- `docs/40-validation/scheduler-model-contract-audit-rev0025.md`.
- `docs/00-meta/cube-audit-rev0025.md`.

Changed/factored:

- Runtime boot reports now expose `crossLaneSchedulerModelProbe`.
- The cross-lane scheduler frontier, future-session office manual, and non-claims charter now include the model-oracle stair and its boundaries.
- Manifest, impact map, surface inventory, package scripts, and research registries now include the model proof.
- Broad release remains browser-light.

Earned:

- Fake-provider `CrossLaneScheduler` generated operations agree with an independent reference model across 18 deterministic scenarios and 3,348 counted operations.
- Future scheduler refactors now have a cheap semantic model guard in addition to the rev0024 fixed scenario proof.

Non-claims: no exhaustive formal verification claim; no true concurrent interleaving or multi-threaded contention proof; no production scheduler claim; no browser Worker scheduler proof; no work stealing, preemption, priority inheritance, deadline scheduling, or DRF implementation claim; no throughput, latency, fairness-SLO, real performance, or cross-browser conformance claim.

## rev0024 — 2026-05-25

Codename: Cross Lane Scheduler Dreambank.

- Added related-work research pass 019 on runtime schedulers, dispatch queues, event loops/threadpools, resource scheduling, browser task priorities, and trace evidence.
- Added `CrossLaneScheduler` as a fake-provider cross-lane contract primitive.
- Added `scheduler:cross-lane-contract-proof`.
- Added `facility:scheduler-contract-audit`.
- Added docs:
  - `docs/05-research/related-work-research-pass-019.md`
  - `docs/20-architecture/runtime-dreambank-019.md`
  - `docs/20-architecture/cross-lane-scheduler-frontier.md`
  - `docs/40-validation/cross-lane-scheduler-slice.md`
  - `docs/40-validation/scheduler-contract-audit-rev0024.md`
  - `docs/00-meta/cube-audit-rev0024.md`
- Added artifacts:
  - `artifacts/validation/REV0035-CROSS-LANE-SCHEDULER-PROBE.json`
  - `artifacts/audit/REV0035-SCHEDULER-CONTRACT-AUDIT.json`
- Updated future-session handoff and non-claims surfaces to keep the scheduler claim narrow.
- Preserved browser-light release posture.

Non-claims: no production scheduler claim; no browser Worker scheduler proof; no real preemption or OS-thread scheduling claim; no work-stealing implementation claim; no OPFS/WebGPU/render/media/cross-tab provider integration proof; no latency, throughput, fairness-SLO, or cross-browser conformance claim.

## rev0023 — 2026-05-25

Codename: Persisted Spill Recovery Dreambank.

This revision resumes feature work after the rev0022 foundation audit. It adds a fake-provider persisted spill recovery rung, then adds a recovery-contract audit/factor so the new claim is wired through source, docs, manifest, impact map, inventory, validation index, research registry, and non-claim surfaces.

Added:

- `src/persisted-spill-mailbox.mjs`.
- `tools/persisted_spill_recovery_probe.mjs`.
- Manifest task `ipc:persisted-spill-recovery-proof`.
- Artifact `artifacts/validation/REV0035-PERSISTED-SPILL-RECOVERY-PROBE.json`.
- `tools/recovery_contract_audit.mjs`.
- Manifest task `facility:recovery-contract-audit`.
- Artifact `artifacts/audit/REV0035-RECOVERY-CONTRACT-AUDIT.json`.
- `docs/05-research/related-work-research-pass-018.md`.
- `docs/20-architecture/runtime-dreambank-018.md`.
- `docs/20-architecture/persisted-spill-recovery-frontier.md`.
- `docs/40-validation/persisted-spill-recovery-slice.md`.
- `docs/40-validation/recovery-contract-audit-rev0023.md`.

Changed/factored:

- `tools/check_cube.py` is now less revision-brittle and checks the current revision/prefix dynamically.
- `tools/audit_cube_surfaces.mjs` now derives expected artifact outputs from the manifest instead of hardcoding one revision's artifact list.
- Runtime exports, IPC exports, smoke tests, type declarations, manifest, impact map, surface inventory, research registries, and handoff docs now include the persisted-spill recovery rung.

Earned claim:

- A fake-provider `PersistedSpillMailbox` can checkpoint ready/pending state, replay a post-checkpoint journal tail, redeliver pending frames after recovery, avoid redelivering acked frames, ignore a torn/corrupt tail record, reject a corrupt manifest, and preserve payload length/checksum agreement in the scripted proof.

Non-claims:

- No OPFS persisted-spill proof.
- No browser Worker persisted-spill proof.
- No browser reload/crash recovery proof.
- No fsync, flush, quota, eviction, or durability claim.
- No exactly-once delivery claim.
- No multi-producer or multi-consumer persisted mailbox proof.
- No throughput or latency claim.
- No cross-browser conformance claim.
- No WebGPU proof.

Next likely slice: cross-lane scheduler contract, or persisted-spill retention/compaction model before OPFS spending.

## rev0022 — 2026-05-25

Codename: Foundation Audit Coherence.

This revision paused feature expansion and audited the cube foundation. It fixed a real affected-selection bug in `tools/run_tests.mjs`, added a release-tier affected-runner dry-run, added a deep foundation audit, clarified future-session handoff, and reinforced current artifact/non-claim discipline.
