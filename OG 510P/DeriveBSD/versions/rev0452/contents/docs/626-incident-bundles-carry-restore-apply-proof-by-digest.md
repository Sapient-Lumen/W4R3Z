# Incident bundles carry restore apply proof by digest

**Tier:** B (Base support/evidence contract)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility, isolation  
**Patterns:** Bundles compose drift surfaces, Plan→Apply→Receipt, Quarantine→Promote  

DeriveBSD already standardized `restore.plan` / `restore.receipt` and decided that ordinary restore stays quarantine-first while `replacement-target` remains a stronger promotion step.
What was still missing was the boring operational join:
**how does the official incident/support bundle contract name the exact restore apply evidence when recovery actually participates in the story?**

This doc makes that join explicit.
It does **not** create a new recovery subsystem or a new product-profile key.
It only keeps the official support handoff from dropping recovery back into notes, shell transcripts, or backend-specific restore-job logs.

See also:
- ADR: `adrs/ADR-0216-incident-bundles-carry-restore-apply-proof-by-digest.md`
- support-bundle contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- evidence spine: `docs/229-evidence-spine-overview.md`
- restore lane: `docs/316-backups-and-restores-as-derived-operations.md`
- restore boundary: `docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md`

## Accepted boundary

Official incident/support bundles may carry restore apply proof by digest.

Concretely:

- `scope.include.restore_receipts` selects whether restore apply evidence belongs in the bounded handoff.
- `includes.restore_receipt_digests` names the exact `restore.receipt` object(s) that belong to that incident.
- The join is **digest-first** and points at the canonical receipt, not at a private restore-job transcript.

Because `bundle.plan.selection.include` already reuses the incident-bundle include-knob surface, the same selector works for deterministic bundle planning too.

## Why this is worth coding toward

This is a small decision, but it closes an expensive operational hole.
Once official incident bundles can carry `restore_receipt_digests`, DeriveBSD can answer recovery-shaped incident questions from the typed handoff itself:

- what restore apply ran,
- whether it stayed quarantine-first,
- whether stronger replacement authority was exercised,
- and which exact digest-bound receipt proves it.

That is the point where restore stops being merely standardized and starts being operationally composable.

Selector note: official bundle planning now uses `scope.include.restore_receipts`, and deterministic bundle plans inherit the same `restore_receipts` knob through the shared include surface.

Last updated: 2026-03-21r356
