# ADR-0215: Incident bundles carry event-seal proof by digest

- Status: Accepted
- Date: 2026-03-21

## Context

`ADR-0213` and `docs/623-event-journal-digests-stay-chain-exact-and-seal-list-bound.md` already fixed the **exact proof recipe** for the local event lane:

- `event.record.prev_digest` now binds the exact previous stored record,
- `event.segment.chain_head_digest` now binds an exact continuity envelope,
- and `event.seal.receipt.segments_root_digest` now binds an exact ordered segment list.

That still left one practical support/export gap:
**the official incident/support bundle contract could include bounded `event.segment` references, but it still had no typed place for the `event.seal.receipt` digests that prove those segments participated in a tamper-evident sealing lane.**

That omission is expensive because it quietly re-opens the same folklore boundary `ADR-0213` closed:

- support bundles can carry segment digests without carrying the sealing proof that commits those segments as an ordered set,
- responders fall back to verifier-specific seal exports, journalctl screenshots, or local shell archaeology to explain whether continuity was protected,
- event sealing remains an optional lane in prose but disappears from the official support handoff right where incident integrity matters most,
- and exact segment/chain/seal rules stop composing with the official incident-bundle contract.

The archive already has the right pattern for this.
We do **not** need a new logging subsystem.
We need the official incident-bundle selector and metadata surfaces to carry the typed seal proof by digest.

## Decision

**Incident/support bundles may carry event-seal proof by typed digest joins.**

Specifically:

1. Extend the canonical bundle include-knob surface.
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` must carry `event_seal_receipts`.
   - Because `bundle.plan.selection.include` reuses that shape, official bundle planning inherits the same selector automatically.

2. Extend the canonical bundle metadata surface.
   - `incident.bundle.includes` must carry `event_seal_receipt_digests`.
   - These digests point at `event.seal.receipt` objects, not at tool-private verification dumps.

3. Keep segment selection and seal proof distinct inside support handoff.
   - `event_segments` keep naming the bounded segment window support is looking at.
   - `event_seal_receipt_digests` name the exact seal receipts that commit those segments into a tamper-evident ordered set.
   - Neither field replaces the event timeline or any later human summary surface.

4. Keep the rule conditional and narrow.
   - Incident bundles should include recent event-seal receipts **when sealing is enabled and continuity proof matters to the incident/support story**.
   - This does not mean every bundle must always include every historical seal receipt.

5. Do not promote verifier-private outputs into the authority model.
   - The official join is bounded segment references plus digest(s) of `event.seal.receipt`.
   - Raw verifier output, tool-specific key dumps, or local shell transcripts remain explicit stronger/debugging evidence, not the default bundle truth.

## Consequences

- Support bundles can now answer both **which event segments are in scope** and **what tamper-evident seal proof covered them**.
- The official support handoff stays aligned with `ADR-0213` instead of partially undoing it.
- `bundle.plan` / `incident.bundle` remain the one official bundle-selection and metadata contract for this evidence lane too.
- Future incident/debug/export flows no longer need verifier-specific folklore just to explain whether bounded event history was seal-protected.

## What this does not decide

This ADR does **not** decide:

- whether every product profile enables event sealing by default,
- the final retention window for old seal receipts,
- the stronger export path for raw verifier diagnostics,
- or the final UX for displaying seal coverage inside support tooling.

It only fixes the missing typed join between the already-decided `event.seal.receipt` artifact and the already-decided incident/support bundle contract.
