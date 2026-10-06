# Kernel Kit usefulness scorecard frontier — rev0044

The Kernel Kit demo must answer a harsher question than "did the stages pass?"
It must answer: **who would care, what evidence is earned, and what remains unproven?**

Rev0044 adds a release-tier usefulness scorecard so the demo is not only a
browser/CDP proof path. It becomes a small decision surface for future sessions.

## New runtime noun

```txt
KernelKitDemoUsefulnessReport
```

It is built by `createKernelKitDemoUsefulnessReport()` and validated by
`validateKernelKitDemoUsefulnessReport()`.

## Required sections

```txt
beneficiary-fit
workflow-scorecard
earned-evidence
missing-evidence
next-demo-gate
non-claims
```

## Workflows scored

```txt
runtime-control-plane
worker-compute-agent
data-plane-object-ref
overload-governance
storage-lane-provider
trace-receipt
```

The scorecard is intentionally evidence-based. A workflow is earned by proof
booleans and/or trace kinds, not by prose.

## Beneficiaries

The report maps the evidence to four likely beneficiary groups:

- browser IDE and agent-workbench builders;
- heavy local web app builders;
- local-first storage/tool builders;
- runtime-library authors.

This is not user research. It is a local fit hypothesis based on the current
proof surface.

## Why this matters

The Kernel Kit demo was in danger of becoming a parade of components. The
scorecard turns it into a product-shaped question:

> Can a future session explain why this narrow BrowserRT wedge is useful without
> reading the entire cube?

Rev0044 answers: yes, if the scorecard remains visible beside the proof.

## Non-claims

No user research claim. No adoption evidence claim. No pricing, market-size, or
product-market-fit claim. No claim that this demo is the final product shape. No
production runtime claim. No OPFS durability, cross-browser, mobile-lifecycle, or
performance claim.


## Rev0044 canonical Kernel Kit needles

BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. Kernel Kit Trace Export Workbench. Kernel Kit usefulness scorecard. Current tasks: demo:kernel-kit-usefulness-proof, facility:kernel-kit-usefulness-audit, demo:kernel-kit-observatory-proof, browser:kernel-kit-demo-proof, facility:kernel-kit-observatory-audit, demo:kernel-kit-trace-export-proof, facility:kernel-kit-trace-export-audit. No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.


## Rev0044 non-claims carry-forward

No market validation claim. No user research claim. No adoption evidence claim. No product-market-fit claim. No production runtime claim. No production observability claim. No browser performance claim. No OpenTelemetry compatibility claim. No Chrome DevTools trace-format compatibility claim. No Perfetto compatibility claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No OPFS sync access handle storage-lane proof. No browser Worker OPFS storage-lane provider proof. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.

No local reload handoff durability or crash-recovery claim.


## Audit coherence keys

BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. Kernel Kit Trace Export Workbench. Kernel Kit usefulness scorecard. Kernel Kit controlled failure mode. demo:kernel-kit-failure-mode-proof. demo:kernel-kit-export-bundle-proof. facility:kernel-kit-workbench-contract-audit. demo:kernel-kit-usefulness-proof. facility:kernel-kit-usefulness-audit. demo:kernel-kit-trace-export-proof. facility:kernel-kit-trace-export-audit. demo:kernel-kit-observatory-proof. browser:kernel-kit-demo-proof. facility:kernel-kit-observatory-audit. No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability.

No browser download UX claim.
No failure recovery automation claim.

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


Rev0053 carry-forward readiness non-claims: No production readiness-gate claim. No automated demo-go/no-go claim.
