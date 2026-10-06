# Kernel Kit Support Bundle Privacy Scrub Contract Audit — rev0107

## Purpose

This audit keeps the privacy scrub path wired through runtime, types, browser page, browser probe, release manifest, impact map, surface inventory, package retention, and docs. It prevents the scrub from becoming a decorative helper that is absent from the actual Kernel Kit handoff flow.

Run:

```bash
node tools/run_tests.mjs --tier release --id facility:kernel-kit-support-bundle-privacy-scrub-audit --jobs 1
```

## What the audit checks

- `src/kernel-kit-demo.mjs` exports `createKernelKitSupportBundlePrivacyScrub` and `validateKernelKitSupportBundlePrivacyScrub`.
- `src/browserrt.mjs` imports, exports, and traces runtime convenience calls for the scrub.
- `src/types.d.ts` declares the scrub surface.
- The browser demo page has a support-bundle privacy scrub control and output panel.
- The managed Chromium Kernel Kit probe drives and validates the privacy scrub path.
- The release support-bundle proof requires the embedded scrub to validate.
- Package release retention includes the privacy scrub proof and audit artifacts.

## Non-claims

This audit only proves wiring and invariant checks. It does not claim anonymization, production privacy, side-channel mitigation, telemetry ingestion safety, authenticity, signing, or full data-loss-prevention coverage.

This checkpoint is not side-channel mitigation and must not be presented as telemetry-ingestion privacy hardening.

Audit-visible privacy scrub non-claims:

- No production support-bundle privacy claim.
- No anonymization, differential-privacy, or irreversible de-identification claim.
