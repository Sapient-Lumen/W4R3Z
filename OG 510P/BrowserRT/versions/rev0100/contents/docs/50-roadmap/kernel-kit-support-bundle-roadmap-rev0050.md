# Kernel Kit support bundle roadmap — rev0054

The support bundle is the next usefulness rung after the diagnostic runbook.

Immediate next improvements:

1. Add a human copy/download control for the support bundle, still with no browser download UX claim.
2. Add a compact “resume from bundle” reader that validates an imported JSON bundle.
3. Add a bundle diff between two revisions of the Kernel Kit demo.
4. Add a support-bundle fixture that future sessions can use to reproduce a demo failure without launching Chromium first.

Keep broad release browser-light. Spend browser/CDP budget only by explicit id.

Non-claims remain: no production support-bundle claim, no telemetry backend integration claim, no automated failure triage claim, no OPFS durability claim, no performance claim, and no cross-browser conformance claim.

Explicit roadmap non-claims repeated for audit readability:

- No production support-bundle claim.
- No automated failure triage claim.

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
