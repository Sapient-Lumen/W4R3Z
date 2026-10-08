# Clippy Safety Profile & Waiver lane boundaries — 2026-03-22

This note keeps **P-0459 Clippy Safety Profile & Waiver Kit** from collapsing into neighboring lanes.

## What belongs in P-0459

P-0459 owns:
- lint-policy authority receipts,
- checked-scope matrices,
- diagnostic-channel receipts,
- waiver decision records,
- and portable lint support bundles.

## What does not belong here

### Not the same as P-0473 Cargo Lints Adoption Receipt Kit
P-0473 is the workspace-rollout / inheritance-cleanup lane.
P-0459 is narrower and more evidence-oriented: it focuses on what a safety-critical or high-assurance lint claim really means at review time.

### Not the same as Clippy itself
Clippy defines and emits lints.
P-0459 exists to publish **reviewable contract artifacts** above those lints.

### Not the same as Cargo manifest lint configuration
Cargo `[lints]` and `workspace.lints` are policy knobs.
P-0459 exists because those knobs still do not answer scope, channel, or waiver questions by themselves.

### Not the same as P-0120 Unsafe Contract Auditor Kit
P-0120 maps broader unsafe obligations and witness fidelity.
P-0459 may import lint findings relevant to unsafe posture, but it does not replace broader unsafe evidence.

## Guardrails

Do not let any of the following stand in for an honest lint-policy contract:
- “the workspace forbids `unsafe_code`,”
- “`cargo clippy` passed,”
- “Clippy is configured,”
- “the waiver is written down,”
- or “nightly found nothing extra.”

A crate can have all of those truths and still leave policy authority, checked scope, finding provenance, or waiver ownership unresolved.
