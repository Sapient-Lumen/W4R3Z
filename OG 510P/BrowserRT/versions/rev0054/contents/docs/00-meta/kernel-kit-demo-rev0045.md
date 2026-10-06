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

## rev0047 diagnostic runbook carry-forward

Kernel Kit diagnostic runbook. `demo:kernel-kit-diagnostic-runbook-proof`. `facility:kernel-kit-diagnostic-runbook-audit`.

The diagnostic runbook is a future-session handoff that turns success/failure trace comparison into exact next commands. It is not root-cause automation.

No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No root-cause analysis claim. No automated failure recovery claim. Broad release remains browser-light.

