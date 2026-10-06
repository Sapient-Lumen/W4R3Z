# START HERE — BrowserRT rev0054

Current packaged head: `rev0054`

Current office: **Kernel Kit Readiness Contrast Workbench**.

Start with:

```bash
make turn-start
node tools/run_tests.mjs --tier release --id demo:kernel-kit-readiness-contrast-proof,facility:kernel-kit-readiness-contrast-audit --jobs 1
```

Run the explicit browser demo only when browser/CDP budget is intentional:

```bash
node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1
```

What rev0054 adds: the demo can now build a passing readiness gate and a deliberately degraded readiness gate, then explain which gates changed and why the weaker handoff must not be trusted.

Do not erase these boundaries: No production readiness-contrast claim. No automated regression detection claim. No automated demo-go/no-go claim. No production runtime claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.


## Full Kernel Kit non-claims carried forward

No production handoff-markdown claim. No production handoff-markdown import claim. No production readiness-gate claim. No production readiness-contrast claim. No automated regression detection claim. No automated demo-go/no-go claim. No automated next-session correctness claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim. No production support-bundle claim. No production support-bundle import claim. No production support-bundle diff claim. No production guided-tour claim. No automated failure triage claim. No support-bundle authenticity or signature claim. No automated demo correctness claim.
