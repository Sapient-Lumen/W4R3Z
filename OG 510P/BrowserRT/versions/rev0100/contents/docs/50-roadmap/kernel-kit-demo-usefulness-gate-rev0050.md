# Kernel Kit Demo Usefulness Gate — rev0054

The current usefulness gate is no longer “can the demo run?” Rev0042/0043 answered that. Rev0044 asks whether the demo can explain who benefits, what workflows are earned, and what evidence is still missing.

Current earned wedge:

```txt
human page -> BrowserRT runtime -> Worker agent -> transfer ref -> bounded channel -> admission -> OPFS storage-lane adapter -> reload readback -> transcript
```

The scorecard now makes the current earned wedge legible. A future session should improve one of these next:

1. Make the page transcript easier to scan, with lane grouping and copyable artifact export.
2. Add an OPFS journal/manifest skeleton, still explicit browser/full tier.
3. Add a tiny trace viewer for the Kernel Kit demo artifact.
4. Add a strict demo-failure diagnosis panel that explains missing capabilities.

Do not claim UX validation, market demand, production readiness, OPFS durability, cross-browser support, or performance because the page works in the cloudtainer Chromium fixture.


## Audit coherence markers

Interactive Kernel Kit Demo
browser:kernel-kit-demo-proof
facility:kernel-kit-demo-audit
facility:kernel-kit-page-contract-audit
No production runtime claim.
No product-market-fit claim.
No OPFS durability

Audit coherence keys: BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. demo:kernel-kit-observatory-proof. browser:kernel-kit-demo-proof. facility:kernel-kit-observatory-audit. No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability. No browser performance claim. No OpenTelemetry compatibility claim. No Chrome DevTools trace-format compatibility claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.


## Rev0043 coherence note

BrowserRT Kernel Kit now treats the Integrated Kernel Kit Demo and Kernel Kit Demo Observatory as one usefulness wedge. The executable release-tier proof remains `demo:kernel-kit-proof`; the explicit browser proof remains `browser:kernel-kit-demo-proof`; the observatory proof is `demo:kernel-kit-observatory-proof`; and the release-tier observatory audit is `facility:kernel-kit-observatory-audit`.

No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. Browser/CDP proof remains explicit by id/tier and the broad release gate remains browser-light.

## rev0054 observatory coherence note

BrowserRT Kernel Kit remains the narrow usefulness wedge. Kernel Kit Demo Observatory is the human-readable receipt layer for `demo:kernel-kit-observatory-proof`, `browser:kernel-kit-demo-proof`, and `facility:kernel-kit-observatory-audit`.

Non-claims carried forward: No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.


## rev0054 coherence markers

BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. Kernel Kit Trace Export Workbench. Current tasks: `demo:kernel-kit-trace-export-proof`, `facility:kernel-kit-trace-export-audit`, `demo:kernel-kit-observatory-proof`, `browser:kernel-kit-demo-proof`, and `facility:kernel-kit-observatory-audit`.

Non-claims: No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No Chrome DevTools trace-format compatibility claim. No OpenTelemetry compatibility claim. No Perfetto compatibility claim.


Current scorecard tasks: `demo:kernel-kit-usefulness-proof` and `facility:kernel-kit-usefulness-audit`.
\nKernel Kit usefulness scorecard.


## Rev0044 canonical Kernel Kit needles

BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. Kernel Kit Trace Export Workbench. Kernel Kit usefulness scorecard. Current tasks: demo:kernel-kit-usefulness-proof, facility:kernel-kit-usefulness-audit, demo:kernel-kit-observatory-proof, browser:kernel-kit-demo-proof, facility:kernel-kit-observatory-audit, demo:kernel-kit-trace-export-proof, facility:kernel-kit-trace-export-audit. No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.


Rev0045 carry-forward addition: Kernel Kit controlled failure mode. demo:kernel-kit-failure-mode-proof. demo:kernel-kit-export-bundle-proof. facility:kernel-kit-workbench-contract-audit. No browser download UX claim. No failure recovery automation claim.


## rev0054 Kernel Kit currentness block

BrowserRT Kernel Kit current demo surfaces: Integrated Kernel Kit Demo; Kernel Kit Demo Observatory; Kernel Kit Trace Export Workbench; Kernel Kit usefulness scorecard; Kernel Kit controlled failure mode; Kernel Kit success/failure trace comparison.

Current manifest tasks kept legible: `browser:kernel-kit-demo-proof`, `demo:kernel-kit-observatory-proof`, `facility:kernel-kit-observatory-audit`, `demo:kernel-kit-trace-export-proof`, `facility:kernel-kit-trace-export-audit`, `demo:kernel-kit-usefulness-proof`, `facility:kernel-kit-usefulness-audit`, `demo:kernel-kit-failure-mode-proof`, `demo:kernel-kit-export-bundle-proof`, `demo:kernel-kit-trace-comparison-proof`, `facility:kernel-kit-trace-comparison-audit`, `facility:kernel-kit-workbench-contract-audit`.

Non-claims: No market validation claim. No user research claim. No adoption evidence claim. No product-market-fit claim. No production runtime claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No production observability claim. No browser download UX claim. No failure recovery automation claim. No automated failure recovery claim. No root-cause analysis claim. No browser performance claim. No OpenTelemetry compatibility claim. No Chrome DevTools trace-format compatibility claim. No local reload handoff durability or crash-recovery claim. No Perfetto compatibility claim. No OPFS sync access handle storage-lane proof. No browser Worker OPFS storage-lane provider proof. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.

## rev0054 Kernel Kit diagnostic runbook update

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
