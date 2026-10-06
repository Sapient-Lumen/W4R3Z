# Future-session office manual — BrowserRT rev0054

Current office: **Kernel Kit Readiness Contrast Workbench**.

Resume with:

```bash
make turn-start
node tools/run_tests.mjs --tier release --id demo:kernel-kit-readiness-contrast-proof,facility:kernel-kit-readiness-contrast-audit --jobs 1
python3 tools/check_cube.py
```

Only spend browser/CDP budget intentionally:

```bash
node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1
```

Rev0054 keeps the Kernel Kit readiness gate but adds a negative contrast. The useful lesson is: a future session should not just see a passing handoff; it should see that a degraded handoff fails visibly and names its missing gates.

Do not claim: production runtime, production readiness contrast, automated regression detection, automated demo go/no-go, automated next-session correctness, product-market fit, OPFS durability/quota/eviction/crash recovery, cross-browser conformance, WebGPU/WebNN/WebTransport/WebRTC evidence, performance/SLO, or exactly-once delivery.


## Full Kernel Kit non-claims carried forward

No production handoff-markdown claim. No production handoff-markdown import claim. No production readiness-gate claim. No production readiness-contrast claim. No automated regression detection claim. No automated demo-go/no-go claim. No automated next-session correctness claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim. No production support-bundle claim. No production support-bundle import claim. No production support-bundle diff claim. No production guided-tour claim. No automated failure triage claim. No support-bundle authenticity or signature claim. No automated demo correctness claim.

No production runtime claim.

## How to resume the office

Run `make turn-start`, then the current contrast proof/audit. Spend browser/CDP only by explicit id.

## Current earned rungs

Kernel Kit demo, support bundle, support-bundle import/diff, guided tour, handoff Markdown, handoff Markdown import, readiness gate, and readiness contrast are earned as browser-light/release-tier or explicit browser proof surfaces.

Persisted-spill recovery remains a fake-provider earned rung, not an OPFS durability claim.

## Do not erase non-claims

Preserve no cross-browser conformance, No WebGPU proof, no OPFS durability/quota/eviction/crash-recovery/browser-restart, and no production runtime/product-market-fit boundaries.

## Earn each stair

Future sessions should add one small proof and one audit, then update manifest, impact map, surface inventory, docs, non-claims, and package validation.
persisted-spill recovery remains fake-provider evidence; it is not OPFS durability.
