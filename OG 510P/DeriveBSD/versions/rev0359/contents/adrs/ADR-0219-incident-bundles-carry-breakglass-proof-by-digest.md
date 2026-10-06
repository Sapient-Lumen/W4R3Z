# ADR-0219: Incident bundles carry breakglass proof by digest

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/236-breakglass-and-recovery-mode.md`, `docs/250-breakglass-and-recovery-workflows.md`, and `spec/breakglass.receipt.schema.json` already made emergency access a typed lane:

- `breakglass.receipt` is the authoritative emergency-access authority record,
- it binds the grant/lease, scope, expiry, and exercised action,
- and earlier archive work already decided the emergency-session recording/detail/export defaults separately in `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`.

That still left one practical support/export gap.
The official incident/support bundle contract *already* had `breakglass_receipts` plus `breakglass_receipt_digests`, but the archive still treated that join as half-real:

- the canonical bundle example carried a placeholder digest,
- `bundle.plan` did not exercise the selector in the canonical example,
- and the support-handoff docs talked around the emergency-access proof instead of teaching it as a first-class bundle join.

That omission is expensive because it quietly pushes responders back toward ticket notes, rescue-shell folklore, or operator memory right after the archive had already paid to define a typed emergency-access lane.

The archive does **not** need a new breakglass subsystem.
It needs the official support-handoff story to treat `breakglass.receipt` as the typed emergency-access authority proof already present in the schema.

## Decision

**Incident/support bundles keep breakglass proof on the typed digest-first contract.**

Specifically:

1. Keep `breakglass.receipts` / `breakglass_receipt_digests` as the official support-bundle join for emergency-access authority proof.
   - The bundle contract names the exact `breakglass.receipt` object(s) that mattered to the incident.
   - The join stays metadata-first.

2. Keep emergency authority proof distinct from richer session evidence.
   - `breakglass_receipt_digests` prove that emergency authority existed and was exercised.
   - Any subordinate terminal/console/session trails remain separate evidence joins; this ADR does not promote them into the primary support-handoff truth surface.

3. Make the canonical examples real instead of placeholder-shaped.
   - `spec/examples/incident.bundle.json` must bind the real canonical `breakglass.receipt` example digest.
   - `spec/examples/bundle.plan.json` must exercise `breakglass_receipts` on the official include surface.

4. Teach the same answer everywhere.
   - The support-bundle, evidence-spine, breakglass, runbook, and hygiene surfaces must all say that official support handoff may carry `breakglass_receipt_digests` when emergency access participated in the story.

## Consequences

- Support bundles can now answer **whether breakglass happened** and **which exact emergency-access authority record bounded it**.
- The emergency-access lane stays distinct from operator-session and remote-assistance session envelopes instead of collapsing them into one generic privileged-session story.
- The archive stops advertising a schema field it does not fully teach or exercise.

## What this does not decide

This ADR does **not** decide:

- any new breakglass artifact kind,
- any richer export path for terminal/console trails,
- whether every bundle template enables `breakglass_receipts` by default,
- or any new product-profile key.

It only makes the already-existing breakglass bundle join real, typed, and guardrailed.
