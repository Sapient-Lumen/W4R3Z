# Kernel Kit usefulness scorecard roadmap — rev0047

The next demo improvements should stay product-shaped:

1. Keep the one-click demo understandable.
2. Add copy/export controls for the BrowserRT receipt.
3. Add an intentional failure-mode toggle without hiding non-claims.
4. Add a tiny "what would this enable?" scenario for a browser IDE or local-first
   tool builder.
5. Only then consider another expensive browser provider slice.

Do not confuse the scorecard with market evidence. Its role is to prevent vague
ambition by making proof and missing evidence visible.


## Rev0044 canonical Kernel Kit needles

BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. Kernel Kit Trace Export Workbench. Kernel Kit usefulness scorecard. Current tasks: demo:kernel-kit-usefulness-proof, facility:kernel-kit-usefulness-audit, demo:kernel-kit-observatory-proof, browser:kernel-kit-demo-proof, facility:kernel-kit-observatory-audit, demo:kernel-kit-trace-export-proof, facility:kernel-kit-trace-export-audit. No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.


## Rev0044 non-claims carry-forward

No market validation claim. No user research claim. No adoption evidence claim. No product-market-fit claim. No production runtime claim. No production observability claim. No browser performance claim. No OpenTelemetry compatibility claim. No Chrome DevTools trace-format compatibility claim. No Perfetto compatibility claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No OPFS sync access handle storage-lane proof. No browser Worker OPFS storage-lane provider proof. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.

No local reload handoff durability or crash-recovery claim.


Rev0045 carry-forward addition: Kernel Kit controlled failure mode. demo:kernel-kit-failure-mode-proof. demo:kernel-kit-export-bundle-proof. facility:kernel-kit-workbench-contract-audit. No browser download UX claim. No failure recovery automation claim.


## rev0047 Kernel Kit currentness block

BrowserRT Kernel Kit current demo surfaces: Integrated Kernel Kit Demo; Kernel Kit Demo Observatory; Kernel Kit Trace Export Workbench; Kernel Kit usefulness scorecard; Kernel Kit controlled failure mode; Kernel Kit success/failure trace comparison.

Current manifest tasks kept legible: `browser:kernel-kit-demo-proof`, `demo:kernel-kit-observatory-proof`, `facility:kernel-kit-observatory-audit`, `demo:kernel-kit-trace-export-proof`, `facility:kernel-kit-trace-export-audit`, `demo:kernel-kit-usefulness-proof`, `facility:kernel-kit-usefulness-audit`, `demo:kernel-kit-failure-mode-proof`, `demo:kernel-kit-export-bundle-proof`, `demo:kernel-kit-trace-comparison-proof`, `facility:kernel-kit-trace-comparison-audit`, `facility:kernel-kit-workbench-contract-audit`.

Non-claims: No market validation claim. No user research claim. No adoption evidence claim. No product-market-fit claim. No production runtime claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No production observability claim. No browser download UX claim. No failure recovery automation claim. No automated failure recovery claim. No root-cause analysis claim. No browser performance claim. No OpenTelemetry compatibility claim. No Chrome DevTools trace-format compatibility claim. No local reload handoff durability or crash-recovery claim. No Perfetto compatibility claim. No OPFS sync access handle storage-lane proof. No browser Worker OPFS storage-lane provider proof. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.

## rev0047 Kernel Kit diagnostic runbook update

BrowserRT Kernel Kit current demo surfaces: Integrated Kernel Kit Demo; Kernel Kit Demo Observatory; Kernel Kit Trace Export Workbench; Kernel Kit usefulness scorecard; Kernel Kit controlled failure mode; Kernel Kit success/failure trace comparison; Kernel Kit diagnostic runbook.

Current manifest tasks kept legible: `browser:kernel-kit-demo-proof`, `demo:kernel-kit-observatory-proof`, `facility:kernel-kit-observatory-audit`, `demo:kernel-kit-trace-export-proof`, `facility:kernel-kit-trace-export-audit`, `demo:kernel-kit-usefulness-proof`, `facility:kernel-kit-usefulness-audit`, `demo:kernel-kit-failure-mode-proof`, `demo:kernel-kit-export-bundle-proof`, `demo:kernel-kit-trace-comparison-proof`, `facility:kernel-kit-trace-comparison-audit`, `demo:kernel-kit-diagnostic-runbook-proof`, `facility:kernel-kit-diagnostic-runbook-audit`, `facility:kernel-kit-workbench-contract-audit`.

The new diagnostic runbook turns a success/failure trace comparison into: what changed, what stayed bounded, and exact next commands to run. It is a future-session handoff, not root-cause automation.

Useful commands:

```bash
node tools/run_tests.mjs --tier release --id demo:kernel-kit-diagnostic-runbook-proof,facility:kernel-kit-diagnostic-runbook-audit --jobs 1
node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1
```

Non-claims: No market validation claim. No user research claim. No adoption evidence claim. No product-market-fit claim. No production runtime claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No production observability claim. No browser download UX claim. No failure recovery automation claim. No automated failure recovery claim. No root-cause analysis claim. No production incident-response claim. No browser performance claim. No OpenTelemetry compatibility claim. No Chrome DevTools trace-format compatibility claim. No local reload handoff durability or crash-recovery claim. No Perfetto compatibility claim. No OPFS sync access handle storage-lane proof. No browser Worker OPFS storage-lane provider proof. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.

