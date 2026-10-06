# Kernel Kit failure/export workbench validation slice — rev0047

Rev0045 adds release-tier and browser-tier validation for the improved human workbench.

## Release-tier slices

- `demo:kernel-kit-failure-mode-proof` runs `tools/kernel_kit_failure_mode_probe.mjs` and validates controlled failure-mode reports for all declared demo failure modes.
- `demo:kernel-kit-export-bundle-proof` runs `tools/kernel_kit_export_bundle_probe.mjs` and validates a BrowserRT export bundle with transcript, trace export, usefulness score, proof summary, and non-claims.
- `facility:kernel-kit-workbench-contract-audit` runs `tools/kernel_kit_workbench_contract_audit.mjs` and validates source/page/tool/doc/manifest wiring without launching Chromium.

## Browser-tier extension

`browser:kernel-kit-demo-proof` now also exercises:

- `window.BrowserRTKernelKitDemo.exportLastReceipt()`
- `window.BrowserRTKernelKitDemo.runFailureMode({ mode: 'missing-handoff' })`

The browser proof remains explicit browser/full tier. Broad release stays browser-light.

## Evidence required

A passing rev0047 workbench must show:

- happy-path integrated demo still passes;
- export bundle validates;
- controlled failure validates;
- failure-mode report says mutation was prevented;
- page controls exist in HTML;
- API names are visible for future CDP/human use;
- non-claims are present in success, failure, bundle, docs, and receipt.

## Non-claims

No production runtime claim. No browser download UX claim. No failure recovery automation claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No browser performance claim. No cross-browser conformance claim.


## Audit coherence keys

BrowserRT Kernel Kit. Integrated Kernel Kit Demo. Kernel Kit Demo Observatory. Kernel Kit Trace Export Workbench. Kernel Kit usefulness scorecard. Kernel Kit controlled failure mode. demo:kernel-kit-failure-mode-proof. demo:kernel-kit-export-bundle-proof. facility:kernel-kit-workbench-contract-audit. demo:kernel-kit-usefulness-proof. facility:kernel-kit-usefulness-audit. demo:kernel-kit-trace-export-proof. facility:kernel-kit-trace-export-audit. demo:kernel-kit-observatory-proof. browser:kernel-kit-demo-proof. facility:kernel-kit-observatory-audit. No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability.

No user research claim.
No adoption evidence claim.
No local reload handoff durability or crash-recovery claim.
No Perfetto compatibility claim.
No market validation claim.
No OpenTelemetry compatibility claim.
No Chrome DevTools trace-format compatibility claim.
No OPFS sync access handle storage-lane proof.
No browser Worker OPFS storage-lane provider proof.
No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim.
No throughput, latency, SLO, or real performance claim.
No exactly-once delivery claim.

## rev0047 diagnostic runbook carry-forward

Kernel Kit diagnostic runbook. `demo:kernel-kit-diagnostic-runbook-proof`. `facility:kernel-kit-diagnostic-runbook-audit`.

The diagnostic runbook is a future-session handoff that turns success/failure trace comparison into exact next commands. It is not root-cause automation.

No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No root-cause analysis claim. No automated failure recovery claim. Broad release remains browser-light.



Rev0053 full current non-claims: No production runtime claim. No production support-bundle claim. No production support-bundle import claim. No production support-bundle diff claim. No production guided-tour claim. No automated failure triage claim. No support-bundle authenticity or signature claim. No automated demo correctness claim. No automated regression detection claim. No production handoff-markdown import claim. No production readiness-gate claim. No automated demo-go/no-go claim. No automated next-session correctness claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.
