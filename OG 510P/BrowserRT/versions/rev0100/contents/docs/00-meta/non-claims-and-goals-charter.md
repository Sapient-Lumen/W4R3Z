# BrowserRT non-claims and goals charter — rev0056

Current office: **OPFS Restart Persistence Proof**.

## Current goal

Make BrowserRT storage and browser coordination claims earnable by replacing assumptions with small executable proofs: clean OPFS restart readback, narrow Web Locks coordination evidence, and visible artifact-budget pressure.

## Current earned claims

- `browser:opfs-restart-persistence-proof` can write, verify, cleanly restart Chromium with the same temporary profile/local origin, read back, verify, delete, and clean up an OPFS content-addressed block.
- `browser:web-locks-coordination-proof` can observe Web Locks request/query availability, exclusive same-name non-overlap, shared same-name co-holding, and page-to-dedicated-Worker handoff in managed Chromium.
- `cube:artifact-budget-audit` checks source byte budget, artifact prefix retention, current-artifact presence, and byte-identical duplicate doc pressure.
- `demo:kernel-kit-readiness-contrast-proof` can still produce a valid readiness contrast.
- `facility:kernel-kit-readiness-contrast-audit` still checks source/page/API/docs/manifest/non-claim wiring.
- `browser:kernel-kit-demo-proof` remains available explicitly and drives the page-level readiness contrast API.
- Broad release remains browser-light.

## Non-claims

No production runtime claim. No production readiness-gate claim. No production readiness-contrast claim. No automated regression detection claim. No automated demo/go-no-go claim. No automated next-session correctness claim. No support-bundle authenticity or signature claim. No telemetry backend ingestion claim. No automated failure triage claim. No root-cause analysis claim. No automated failure recovery claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No Web Locks fairness, background lifecycle, crash recovery, storage-leader, or cross-browser conformance claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.

## Full Kernel Kit non-claims carried forward

No production handoff-markdown claim. No production handoff-markdown import claim. No production readiness-gate claim. No production readiness-contrast claim. No automated regression detection claim. No automated demo/go-no-go claim. No automated next-session correctness claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim. No production support-bundle claim. No production support-bundle import claim. No production support-bundle diff claim. No production guided-tour claim. No automated failure triage claim. No support-bundle authenticity or signature claim. No automated demo correctness claim.

## North-star goal

Make BrowserRT a useful browser-runtime Kernel Kit by earning each local runtime claim through small proofs, audits, and explicit non-claims.

## Current claims that are earned

The Kernel Kit demo can show a positive readiness gate and a degraded-readiness contrast. Persisted-spill recovery is still fake-provider evidence. Async OPFS has managed-Chromium page-reload and clean restart readback evidence. Web Locks has narrow same-origin page/Worker coordination evidence. Broad release remains browser-light.

## Current non-claims

No production runtime, no cross-browser conformance, No WebGPU proof, no OPFS durability/quota/eviction/crash-recovery/browser-restart, no multi-tab storage coordination, no Web Locks fairness/background/crash claim, no product-market fit, and no exactly-once delivery.

## Claim promotion rule

A claim may be promoted only after a source primitive, proof artifact, audit surface, manifest task, docs, and non-claim boundary all agree. Browser/provider claims need repeated cloudtainer evidence or external-device evidence.


rev0062 current note: Web Lock tab-termination evidence is a managed Chromium/CDP target-close proof. It does not prove cross-browser behavior, page discard, mobile/background suspension, service-worker lifecycle, browser crash recovery, fairness, OPFS durability, quota, eviction, or production readiness. `BRT_WEB_LOCK_TIMEOUT` remains an acquisition-only backstop from the carried-forward timeout slice.
