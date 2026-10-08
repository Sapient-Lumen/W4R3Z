## rev0342 — decision-review-bundle-handoff-promotion-refactor — 2026-06-18

- Added an exportable decision review bundle for the signed sandbox positive path.
- Included public trust-store view, producer contracts, evidence payloads, attestations, verifier packets, replay hashes, promotion summaries, and held decision-output status.
- Audited the exported packet by independently re-verifying embedded evidence, proving tamper failure, and checking that no private key material is exported.
- Added the review-bundle audit to the truth-boundary semantic audit group.
- Refreshed the signed smoke producer/key/locator labels from rev0341 to rev0342.

# Changelog

## Compact revision ledger

| Revision | Date | Codename | Summary |
|---|---|---|---|
| rev0342 | 2026-06-18 | decision-review-bundle-handoff-promotion-refactor | Added a bounded, independently re-verifiable decision review handoff bundle for the sandbox positive path. |
| rev0341 | 2026-06-18 | strict-positive-evidence-proof-gate-promotion-refactor | Expanded the positive evidence path to strict default-scope proofs and hardened promotion summaries. |
| rev0340 | 2026-06-18 | positive-evidence-scope-gate-promotion-refactor | Added a signed sandbox positive evidence path and blocked non-default route-limit promotion outside sandbox. |
| rev0339 | 2026-06-18 | adapter-binding-trust-policy-promotion-refactor | Bound signed external evidence to exact adapter scope, added trust-policy failures, and hardened replay/promotion/output audits. |
| rev0338 | 2026-06-18 | external-attestation-verifier-streaming-audit-refactor | Added a concrete external-attestation verifier boundary, blocked self-certified verified labels, and bound verifier status into replay/promotion/output hashes. |
| rev0337 | 2026-06-18 | evidence-truth-boundary-release-lineage-refactor | Separated schema fixtures from external evidence, made attestation verification fail-closed, held all built-in cases, repaired lineage, and reduced repeated audit work. |
| rev0336 | 2026-06-18 | decision-output-materialization-hold-reasons-refactor | Added decision-output packets; its internal-fixture finalization counts are superseded by rev0337. |
| rev0335 | 2026-06-18 | decision-promotion-gate-finalization-refactor | Added promotion gates; its internal-fixture promotion counts are superseded by rev0337. |
| rev0334 | 2026-06-18 | evidence-replay-ledger-drift-audit-refactor | Added replay ledgers and tamper checks. |
| rev0333 | 2026-06-18 | authority-source-manifest-strict-intake-refactor | Added authority-source manifest gates. |
| rev0332 | 2026-06-18 | authority-intake-provenance-real-source-gate-refactor | Added raw authority-intake provenance gates. |
| rev0331 | 2026-06-18 | authority-evidence-strict-execution-gate-refactor | Added strict authority evidence interfaces. |
| rev0330 | 2026-06-18 | input-source-certification-strict-model-gate-refactor | Added model-input source certification interfaces. |
| rev0329 | 2026-06-18 | model-input-execution-assumption-boundary-refactor | Required explicit model-input bundles for local execution. |
| rev0328 | 2026-06-18 | evidence-producer-execution-model-runner-refactor | Added a reusable evidence producer runner and local reference execution path. |
