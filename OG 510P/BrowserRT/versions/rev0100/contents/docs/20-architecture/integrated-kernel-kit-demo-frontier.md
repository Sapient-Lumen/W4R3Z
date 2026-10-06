# Integrated Kernel Kit Demo Frontier — rev0044

BrowserRT should prove usefulness through a small integrated product-shaped flow, not only through isolated primitives.

Rev0043 frontier:

```txt
human page
  -> BrowserRT boot
  -> bounded control channel
  -> browser Worker agent
  -> transferable object ref
  -> admission controller
  -> OPFS block store through storage-lane adapter
  -> page reload readback
  -> transcript + trace + non-claims
```

The important refactor is architectural: `demo/kernel-kit-demo-runner.mjs` is now the canonical browser demo path. The CDP probe and the human page share that runner. This prevents the demo from drifting into two realities: one pretty page and one hidden proof script.

Canonical surfaces:

- `demo/kernel-kit-demo.html` is the human-facing page.
- `demo/kernel-kit-demo-runner.mjs` is the browser demo module.
- `tools/browser_kernel_kit_demo_probe.mjs` drives the page module through CDP.
- `src/kernel-kit-demo.mjs` owns the plan, stage labels, transcript contract, proof validation, and non-claims.
- `tools/kernel_kit_demo_contract_audit.mjs` audits the integrated contract.
- `tools/kernel_kit_page_contract_audit.mjs` audits the page runner statically.

Design rule:

```txt
The browser demo proof should call the same page API a human can call.
```

Future improvements should add observability, trace display, failure diagnosis, and artifact export to the page runner rather than duplicating proof logic in tools.

Non-claims remain stronger than the demo claim: no production runtime, UX validation, product-market fit, OPFS durability, performance, or cross-browser claim.


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

## rev0044 observatory coherence note

BrowserRT Kernel Kit remains the narrow usefulness wedge. Kernel Kit Demo Observatory is the human-readable receipt layer for `demo:kernel-kit-observatory-proof`, `browser:kernel-kit-demo-proof`, and `facility:kernel-kit-observatory-audit`.

Non-claims carried forward: No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.


## rev0044 coherence markers

BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. Kernel Kit Trace Export Workbench. Current tasks: `demo:kernel-kit-trace-export-proof`, `facility:kernel-kit-trace-export-audit`, `demo:kernel-kit-observatory-proof`, `browser:kernel-kit-demo-proof`, and `facility:kernel-kit-observatory-audit`.

Non-claims: No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No Chrome DevTools trace-format compatibility claim. No OpenTelemetry compatibility claim. No Perfetto compatibility claim.
\nKernel Kit usefulness scorecard.


## Rev0044 canonical Kernel Kit needles

BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. Kernel Kit Trace Export Workbench. Kernel Kit usefulness scorecard. Current tasks: demo:kernel-kit-usefulness-proof, facility:kernel-kit-usefulness-audit, demo:kernel-kit-observatory-proof, browser:kernel-kit-demo-proof, facility:kernel-kit-observatory-audit, demo:kernel-kit-trace-export-proof, facility:kernel-kit-trace-export-audit. No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.


## Audit coherence keys

BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. Kernel Kit Trace Export Workbench. Kernel Kit usefulness scorecard. Kernel Kit controlled failure mode. demo:kernel-kit-failure-mode-proof. demo:kernel-kit-export-bundle-proof. facility:kernel-kit-workbench-contract-audit. demo:kernel-kit-usefulness-proof. facility:kernel-kit-usefulness-audit. demo:kernel-kit-trace-export-proof. facility:kernel-kit-trace-export-audit. demo:kernel-kit-observatory-proof. browser:kernel-kit-demo-proof. facility:kernel-kit-observatory-audit. No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability.


## rev0047 Kernel Kit currentness block

BrowserRT Kernel Kit current demo surfaces: Integrated Kernel Kit Demo; Kernel Kit Demo Observatory; Kernel Kit Trace Export Workbench; Kernel Kit usefulness scorecard; Kernel Kit controlled failure mode; Kernel Kit success/failure trace comparison.

Current manifest tasks kept legible: `browser:kernel-kit-demo-proof`, `demo:kernel-kit-observatory-proof`, `facility:kernel-kit-observatory-audit`, `demo:kernel-kit-trace-export-proof`, `facility:kernel-kit-trace-export-audit`, `demo:kernel-kit-usefulness-proof`, `facility:kernel-kit-usefulness-audit`, `demo:kernel-kit-failure-mode-proof`, `demo:kernel-kit-export-bundle-proof`, `demo:kernel-kit-trace-comparison-proof`, `facility:kernel-kit-trace-comparison-audit`, `facility:kernel-kit-workbench-contract-audit`.

Non-claims: No market validation claim. No user research claim. No adoption evidence claim. No product-market-fit claim. No production runtime claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No production observability claim. No browser download UX claim. No failure recovery automation claim. No automated failure recovery claim. No root-cause analysis claim. No browser performance claim. No OpenTelemetry compatibility claim. No Chrome DevTools trace-format compatibility claim. No local reload handoff durability or crash-recovery claim. No Perfetto compatibility claim. No OPFS sync access handle storage-lane proof. No browser Worker OPFS storage-lane provider proof. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.

## rev0047 diagnostic runbook carry-forward

Kernel Kit diagnostic runbook. `demo:kernel-kit-diagnostic-runbook-proof`. `facility:kernel-kit-diagnostic-runbook-audit`.

The diagnostic runbook is a future-session handoff that turns success/failure trace comparison into exact next commands. It is not root-cause automation.

No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No root-cause analysis claim. No automated failure recovery claim. Broad release remains browser-light.


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
