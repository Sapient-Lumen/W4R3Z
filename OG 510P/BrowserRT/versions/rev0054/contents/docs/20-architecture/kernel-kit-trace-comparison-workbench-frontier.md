# Kernel Kit success/failure trace comparison frontier — rev0047

Rev0046 improves the Kernel Kit demo by making the difference between the happy path and a controlled failure path visible side-by-side.

The workbench now has a narrow comparison contract:

```txt
success report + controlled failure report
  -> trace-kind sets
  -> stage-status rows
  -> success-only trace kinds
  -> failure-only trace kinds
  -> bounded-failure proof
  -> explicit non-claims
```

This is intentionally a teaching and audit surface. It helps future sessions answer: what work happened, what failed, what stayed bounded, and which claims remain forbidden.

## What the comparison earns

- A success path can show worker/object-ref/storage-lane/reload/trace work.
- A controlled failure path can show failure reporting and prevented mutation.
- The page exposes the same comparison API that the browser/CDP proof drives.
- The release tier has a cheap proof and contract audit for the comparison shape.

## What it does not earn

- No automated failure recovery claim.
- No root-cause analysis claim.
- No production observability claim.
- No Chrome DevTools trace-format compatibility claim.
- No OpenTelemetry compatibility claim.
- No OPFS durability, quota, eviction, crash-recovery, or browser-restart claim.

## Future improvement

The next useful step is making the comparison visually filterable by lane, stage, and mutation boundary without adding production-observability claims.


## rev0047 Kernel Kit currentness block

BrowserRT Kernel Kit current demo surfaces: Integrated Kernel Kit Demo; Kernel Kit Demo Observatory; Kernel Kit Trace Export Workbench; Kernel Kit usefulness scorecard; Kernel Kit controlled failure mode; Kernel Kit success/failure trace comparison.

Current manifest tasks kept legible: `browser:kernel-kit-demo-proof`, `demo:kernel-kit-observatory-proof`, `facility:kernel-kit-observatory-audit`, `demo:kernel-kit-trace-export-proof`, `facility:kernel-kit-trace-export-audit`, `demo:kernel-kit-usefulness-proof`, `facility:kernel-kit-usefulness-audit`, `demo:kernel-kit-failure-mode-proof`, `demo:kernel-kit-export-bundle-proof`, `demo:kernel-kit-trace-comparison-proof`, `facility:kernel-kit-trace-comparison-audit`, `facility:kernel-kit-workbench-contract-audit`.

Non-claims: No market validation claim. No user research claim. No adoption evidence claim. No product-market-fit claim. No production runtime claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No production observability claim. No browser download UX claim. No failure recovery automation claim. No automated failure recovery claim. No root-cause analysis claim. No browser performance claim. No OpenTelemetry compatibility claim. No Chrome DevTools trace-format compatibility claim. No local reload handoff durability or crash-recovery claim. No Perfetto compatibility claim. No OPFS sync access handle storage-lane proof. No browser Worker OPFS storage-lane provider proof. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.

Compatibility carry-forward: controlled failure, export bundle, No production runtime claim, No OPFS durability.

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
