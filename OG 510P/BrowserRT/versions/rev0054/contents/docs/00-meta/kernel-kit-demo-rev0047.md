# BrowserRT Kernel Kit demo — rev0047

Rev0045 improves the Kernel Kit demo as a human-facing workbench rather than a happy-path-only proof.

What changed:

- The page still proves the narrow integrated Kernel Kit path: runtime boot, bounded channel, browser Worker agent, transfer object ref, admission gate, OPFS storage-lane write/read, reload handoff, trace receipt, and usefulness scorecard.
- The page now exposes explicit export controls through `window.BrowserRTKernelKitDemo.exportLastReceipt()` and the `export-kernel-kit-receipt` button.
- The page now exposes a controlled failure path through `window.BrowserRTKernelKitDemo.runFailureMode()` and the `run-kernel-kit-failure` button.
- The browser proof drives those page APIs directly so future sessions do not have to trust hidden harness-only behavior.
- Release-tier probes validate failure-mode receipts and export bundles without launching Chromium.

Why this matters:

The demo should make BrowserRT's value visible in both success and failure. A runtime substrate that only shows green paths is less useful to future users than one that shows how it rejects work, preserves non-claims, emits receipts, and keeps mutation boundaries visible.

Current non-claims remain explicit:

- No production runtime claim.
- No product-market-fit claim.
- No production observability claim.
- No browser download UX claim.
- No failure recovery automation claim.
- No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.
- No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim.
- No throughput, latency, SLO, or real performance claim.


## Audit coherence keys

BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. Kernel Kit Trace Export Workbench. Kernel Kit usefulness scorecard. Kernel Kit controlled failure mode. demo:kernel-kit-failure-mode-proof. demo:kernel-kit-export-bundle-proof. facility:kernel-kit-workbench-contract-audit. demo:kernel-kit-usefulness-proof. facility:kernel-kit-usefulness-audit. demo:kernel-kit-trace-export-proof. facility:kernel-kit-trace-export-audit. demo:kernel-kit-observatory-proof. browser:kernel-kit-demo-proof. facility:kernel-kit-observatory-audit. No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability.

## Rev0045 carry-forward demo contract notes

Interactive Kernel Kit Demo. browser:kernel-kit-demo-proof. facility:kernel-kit-demo-audit. facility:kernel-kit-page-contract-audit.


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

