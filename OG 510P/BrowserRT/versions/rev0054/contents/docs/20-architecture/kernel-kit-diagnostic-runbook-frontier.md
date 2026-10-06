# BrowserRT Kernel Kit diagnostic runbook frontier — rev0047

Current revision: rev0054

## Why this exists

The Kernel Kit Demo Observatory now proves more than a happy path. Rev0047 adds a **diagnostic runbook** that turns the Kernel Kit success/failure trace comparison into a small human handoff: what changed, what stayed bounded, and which exact commands a future session should run next.

This is deliberately not root-cause automation. The goal is to make the workbench more useful to a future maintainer who has less context than the previous session.

## New runtime surface

- `createKernelKitDiagnosticRunbook()`
- `validateKernelKitDiagnosticRunbook()`
- `KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT`
- `KERNEL_KIT_DIAGNOSTIC_RUNBOOK_NON_CLAIMS`
- runtime convenience method marker: `kernelKitDiagnosticRunbook`

## Demo page surface

The human page now exposes:

- `window.BrowserRTKernelKitDemo.compareTraces()`
- `window.BrowserRTKernelKitDemo.diagnoseTraceComparison()`
- a `diagnose-kernel-kit-traces` control;
- a `kernel-kit-diagnostic-output` panel.

## What the runbook must say

A valid diagnostic runbook must make these things visible:

1. The success path is earned.
2. The controlled failure is bounded.
3. The delta is visible.
4. Exact next commands are present.
5. Non-claims remain visible.

## Non-claims

- No production runtime claim.
- No production observability claim.
- No root-cause analysis claim.
- No automated failure recovery claim.
- No production incident-response claim.
- No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.
- No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim.
- No throughput, latency, SLO, or real performance claim.

Broad release remains browser-light; browser spending is explicit through `browser:kernel-kit-demo-proof`.

## Slice names

- `demo:kernel-kit-diagnostic-runbook-proof`
- `facility:kernel-kit-diagnostic-runbook-audit`
- `browser:kernel-kit-demo-proof`

## audit coherence keys

BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. Kernel Kit Trace Export Workbench. Kernel Kit usefulness scorecard. Kernel Kit controlled failure mode. Kernel Kit success/failure trace comparison. Kernel Kit diagnostic runbook.

Tasks: `browser:kernel-kit-demo-proof`; `demo:kernel-kit-observatory-proof`; `facility:kernel-kit-observatory-audit`; `demo:kernel-kit-trace-export-proof`; `facility:kernel-kit-trace-export-audit`; `demo:kernel-kit-usefulness-proof`; `facility:kernel-kit-usefulness-audit`; `demo:kernel-kit-failure-mode-proof`; `demo:kernel-kit-export-bundle-proof`; `demo:kernel-kit-trace-comparison-proof`; `facility:kernel-kit-trace-comparison-audit`; `demo:kernel-kit-diagnostic-runbook-proof`; `facility:kernel-kit-diagnostic-runbook-audit`; `facility:kernel-kit-workbench-contract-audit`.

No market validation claim. No user research claim. No adoption evidence claim. No product-market-fit claim. No production runtime claim. No production observability claim. No browser download UX claim. No failure recovery automation claim. No automated failure recovery claim. No root-cause analysis claim. No OpenTelemetry compatibility claim. No Chrome DevTools trace-format compatibility claim. No local reload handoff durability or crash-recovery claim. No Perfetto compatibility claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No browser performance claim. No OPFS sync access handle storage-lane proof. No browser Worker OPFS storage-lane provider proof. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.


Rev0048 support-bundle current tasks:

```txt
demo:kernel-kit-support-bundle-proof
facility:kernel-kit-support-bundle-audit
```

Non-claims: No production support-bundle claim. No automated failure triage claim. No production runtime claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.


## Kernel Kit audit vocabulary

BrowserRT Kernel Kit; Integrated Kernel Kit Demo; Kernel Kit Demo Observatory; Kernel Kit Trace Export Workbench; Kernel Kit usefulness scorecard; Kernel Kit controlled failure mode; Kernel Kit success/failure trace comparison; Kernel Kit diagnostic runbook; Kernel Kit support bundle.

Current task vocabulary: demo:kernel-kit-trace-comparison-proof; facility:kernel-kit-trace-comparison-audit; demo:kernel-kit-failure-mode-proof; demo:kernel-kit-export-bundle-proof; demo:kernel-kit-diagnostic-runbook-proof; facility:kernel-kit-diagnostic-runbook-audit; demo:kernel-kit-support-bundle-proof; facility:kernel-kit-support-bundle-audit; facility:kernel-kit-workbench-contract-audit; demo:kernel-kit-usefulness-proof; facility:kernel-kit-usefulness-audit; demo:kernel-kit-trace-export-proof; facility:kernel-kit-trace-export-audit; demo:kernel-kit-observatory-proof; browser:kernel-kit-demo-proof; facility:kernel-kit-observatory-audit.

Non-claims: No market validation claim. No user research claim. No adoption evidence claim. No product-market-fit claim. No production runtime claim. No production observability claim. No browser download UX claim. No failure recovery automation claim. No automated failure recovery claim. No root-cause analysis claim. No OpenTelemetry compatibility claim. No Chrome DevTools trace-format compatibility claim. No local reload handoff durability or crash-recovery claim. No Perfetto compatibility claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No OPFS sync access handle storage-lane proof. No browser Worker OPFS storage-lane provider proof. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim. No browser performance claim. No production support-bundle claim. No automated failure triage claim.


Rev0053 carry-forward readiness non-claims: No production readiness-gate claim. No automated demo-go/no-go claim.
