# AGENTS — BrowserRT rev0054

You are entering the BrowserRT cube at rev0054.

Current revision: rev0054

Current office: **Kernel Kit Readiness Contrast Workbench**.

Respect the office:

- Keep broad release browser-light.
- Use explicit browser tier/id for `browser:kernel-kit-demo-proof`.
- Keep the readiness contrast visible in source, page API, docs, manifest, impact map, surface inventory, and non-claims.
- Do not promote the contrast to production regression detection or automated go/no-go.

Recommended commands:

```bash
make turn-start
node tools/run_tests.mjs --tier release --id demo:kernel-kit-readiness-contrast-proof,facility:kernel-kit-readiness-contrast-audit --jobs 1
python3 tools/check_cube.py
```

Non-claims: No production runtime claim. No production readiness-contrast claim. No automated regression detection claim. No automated demo-go/no-go claim. No automated next-session correctness claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.


## Full Kernel Kit non-claims carried forward

No production handoff-markdown claim. No production handoff-markdown import claim. No production readiness-gate claim. No production readiness-contrast claim. No automated regression detection claim. No automated demo-go/no-go claim. No automated next-session correctness claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim. No production support-bundle claim. No production support-bundle import claim. No production support-bundle diff claim. No production guided-tour claim. No automated failure triage claim. No support-bundle authenticity or signature claim. No automated demo correctness claim.
