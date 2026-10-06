# Kernel Kit demo — rev0054

Rev0048 keeps the Kernel Kit demo as the usefulness proof and adds a portable support bundle.

Current path:

```txt
run demo -> reload readback -> export receipt -> controlled failure -> compare traces -> diagnostic runbook -> support bundle
```

Non-claims: No production runtime claim. No production support-bundle claim. No automated failure triage claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No cross-browser conformance claim. No throughput, latency, SLO, or real performance claim.

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


Interactive Kernel Kit Demo contract markers: facility:kernel-kit-demo-audit; facility:kernel-kit-page-contract-audit.

## rev0054 Kernel Kit support-bundle import reader

The Kernel Kit demo can now build a support bundle and import/validate that bundle again. The page exposes `window.BrowserRTKernelKitDemo.importSupportBundle()`, a paste textarea, and an import-validation panel. Release-tier slices are `demo:kernel-kit-support-bundle-import-proof` and `facility:kernel-kit-support-bundle-import-audit`. This is a bounded future-session reader, not telemetry ingestion, authenticity/signature validation, automated triage, browser download UX, OPFS durability, or a production runtime claim.
