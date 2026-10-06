# Future-session office manual — BrowserRT rev0056

Current office: **OPFS Restart Persistence Proof**.

Resume with:

```bash
make turn-start
node tools/run_tests.mjs --tier browser --id browser:opfs-restart-persistence-proof,browser:web-locks-coordination-proof --jobs 1
node tools/artifact_budget_audit.mjs --json artifacts/audit/REV0056-ARTIFACT-BUDGET-AUDIT.json
python3 tools/check_cube.py
```

Only spend browser/CDP budget intentionally. Broad release remains browser-light; OPFS restart and Web Locks coordination proofs are explicit browser-tier tasks.

Rev0056 adds a clean OPFS browser-process restart readback proof, a narrow Web Locks coordination primitive proof, and an artifact-budget/duplicate-doc compaction audit. The useful lesson is: next sessions should reduce risky missing browser/storage evidence and package waste, not clone another set of rev-specific registry docs.

Do not claim: production runtime, OPFS durability/fsync/quota/eviction/crash recovery, multi-tab storage coordination, Web Locks fairness/background/crash behavior, cross-browser conformance, WebGPU/WebNN/WebTransport/WebRTC evidence, performance/SLO, or exactly-once delivery.

## Full Kernel Kit non-claims carried forward

No production handoff-markdown claim. No production handoff-markdown import claim. No production readiness-gate claim. No production readiness-contrast claim. No automated regression detection claim. No automated demo/go-no-go claim. No automated next-session correctness claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim. No production support-bundle claim. No production support-bundle import claim. No production support-bundle diff claim. No production guided-tour claim. No automated failure triage claim. No support-bundle authenticity or signature claim. No automated demo correctness claim.

No production runtime claim.

## How to resume the office

Run `make turn-start`, then the explicit OPFS restart and Web Locks browser proofs by id. Run the artifact budget audit before packaging. Spend browser/CDP only by explicit id.

## Current earned rungs

Kernel Kit demo, support bundle, support-bundle import/diff, guided tour, handoff Markdown, handoff Markdown import, readiness gate, and readiness contrast are earned as browser-light/release-tier or explicit browser proof surfaces.

Persisted-spill recovery remains a fake-provider earned rung, not an OPFS durability claim.

The async OPFS block-store provider has page-reload and clean browser-process restart readback evidence in managed Chromium. Web Locks coordination has narrow exclusive/shared/page-to-Worker evidence in managed Chromium.

## Do not erase non-claims

Preserve no cross-browser conformance, No WebGPU proof, no OPFS durability/quota/eviction/crash-recovery/browser-restart, no production runtime/product-market-fit boundaries, no Web Locks fairness/background/crash claim, and no exactly-once delivery claim.

## Earn each stair

Future sessions should add one small proof and one audit/refactor, then update manifest, impact map, surface inventory, docs, non-claims, and package validation. Prefer quota/eviction, crash/kill recovery, or multi-tab storage-leader integration next.

persisted-spill recovery remains fake-provider evidence; it is not OPFS durability.


rev0062 current note: Web Lock tab-termination evidence is a managed Chromium/CDP target-close proof. It does not prove cross-browser behavior, page discard, mobile/background suspension, service-worker lifecycle, browser crash recovery, fairness, OPFS durability, quota, eviction, or production readiness. `BRT_WEB_LOCK_TIMEOUT` remains an acquisition-only backstop from the carried-forward timeout slice.
