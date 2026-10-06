# ADR-0216: Incident bundles carry restore apply proof by digest

- Status: Accepted
- Date: 2026-03-21

## Context

`ADR-0210` and `docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md` already fixed the **restore authority** boundary:

- `restore.plan` and `restore.receipt` are real archive artifacts,
- ordinary restore stays quarantine-first,
- and `replacement-target` remains a stronger promotion lane with typed preconditions.

That still left one practical support/export gap:
**the official incident/support bundle contract could carry backup, fault, event, trust-view, and packet-capture joins, but it still had no typed place for the `restore.receipt` digests that prove what recovery or replacement apply actually happened.**

That omission is expensive because it quietly re-opens the same folklore boundary `ADR-0210` closed:

- support bundles can say that restore mattered without naming the exact `restore.receipt` object,
- responders fall back to ticket notes, shell transcripts, or ad-hoc recovery writeups to reconstruct what actually ran,
- quarantine rehearsal versus `replacement-target` promotion stops composing with the official support handoff right where incidents need it most,
- and the archive pays to standardize restore artifacts without letting the official bundle lane carry them.

The archive already has the right pattern for this.
We do **not** need a new recovery subsystem.
We need the official incident-bundle selector and metadata surfaces to carry the typed restore apply proof by digest.

## Decision

**Incident/support bundles may carry restore apply proof by typed digest joins.**

Specifically:

1. Extend the canonical bundle include-knob surface.
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` must carry `restore_receipts`.
   - Because `bundle.plan.selection.include` reuses that shape, official bundle planning inherits the same selector automatically.

2. Extend the canonical bundle metadata surface.
   - `incident.bundle.includes` must carry `restore_receipt_digests`.
   - These digests point at `restore.receipt` objects, not at operator notes or recovery-tool-private logs.

3. Keep backup proof, restore proof, and replacement authority distinct inside support handoff.
   - `backup.receipt` evidence still explains what source state existed.
   - `restore_receipt_digests` explain what restore apply actually ran.
   - If a restore used `replacement-target`, the `restore.receipt` object remains the place that points at the stronger replacement precondition.

4. Keep the rule conditional and narrow.
   - Incident bundles should include recent restore receipts **when recovery, rehearsal, or live replacement apply participated in the incident/support story**.
   - This does not mean every bundle must always include every historical restore receipt.

5. Do not promote recovery-tool-private output into the authority model.
   - The official join is the digest of `restore.receipt`.
   - Ad-hoc console transcripts, ticket comments, or backend-specific restore-job logs remain explicit stronger/debugging evidence, not the default bundle truth.

## Consequences

- Support bundles can now prove **what restore apply ran**, not just that backup or recovery was discussed.
- The official support handoff stays aligned with `ADR-0210` instead of partially undoing it.
- `bundle.plan` / `incident.bundle` remain the one official bundle-selection and metadata contract for this recovery lane too.
- Future recovery incidents no longer need shell archaeology just to explain whether the system only rehearsed restore or actually performed a stronger replacement apply.

## What this does not decide

This ADR does **not** decide:

- the final retention window for old restore receipts,
- whether every bundle template enables the selector by default,
- the richer export path for raw backend restore logs,
- or the final frontend UX for presenting recovery evidence.

It only fixes the missing typed join between the already-decided `restore.receipt` artifact and the already-decided incident/support bundle contract.
