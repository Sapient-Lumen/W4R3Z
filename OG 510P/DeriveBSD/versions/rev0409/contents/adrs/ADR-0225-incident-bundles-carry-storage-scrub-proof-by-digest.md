# ADR-0225: Incident bundles carry storage-scrub proof by digest

Date: 2026-03-21
Status: Accepted

## Context

`docs/225-storage-health-and-scrubbing-as-evidence.md` already fixed the core storage-integrity lane:

- `storage-pool-inventory` describes bounded pool topology and feature posture,
- `storage-health-snapshot` is the compact current health surface,
- `storage-scrub-receipt` is the authoritative proof of an explicit integrity-verification run,
- and typed `storage-event` records keep scrub/resilver/degrade milestones joined to the structured journal.

The official incident/support-bundle contract still lagged behind that decision in practice.
`incident.bundle` already had selectors and fields for `storage_pool_inventory_digest`, `storage_health_snapshot_digest`, and `storage_scrub_receipt_digests`, but the archive still did not treat the exact `storage.scrub.receipt` as official support-handoff proof when integrity verification, repaired corruption, or degraded storage health materially shaped an incident.
The canonical examples did not bind the real storage digests, and the surrounding docs still made it too easy to retell storage incidents through `zpool status` transcripts, dashboard screenshots, or ticket prose.

That omission is expensive because it blurs three distinct questions:

- what pool topology and feature posture existed,
- what current health state the host believed at handoff time,
- and what exact bounded integrity-verification action happened.

Without an explicit join, responders drift back toward CLI transcripts, screenshots, or operator notes just to answer whether an integrity scrub actually ran, what it found, or what it repaired.

## Decision

**Incident/support bundles may carry storage-integrity proof by typed digest joins.**

1. **Treat the existing storage selectors and metadata fields as official support-handoff surfaces.**
   - `storage_pool_inventory` / `storage_pool_inventory_digest` identify the bounded pool inventory relevant to the incident.
   - `storage_health_snapshot` / `storage_health_snapshot_digest` identify the compact current storage-health state.
   - `storage_scrub_receipts` / `storage_scrub_receipt_digests` identify the exact `storage.scrub.receipt` objects when integrity verification or repair materially shaped the incident/support story.

2. **Make the shared bundle-plan include surface real for storage as well.**
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` already carries `storage_pool_inventory`, `storage_health_snapshot`, and `storage_scrub_receipts`.
   - `bundle.plan.selection.include` must exercise those selectors when support handoff needs storage inventory, current health state, and exact integrity-verification proof instead of retelling the story from `zpool status` output.

3. **Keep inventory, current state, and exact verification proof distinct inside support handoff.**
   - `storage_pool_inventory_digest` is the typed join for bounded pool topology / feature posture.
   - `storage_health_snapshot_digest` is the typed join for current ONLINE/DEGRADED/FAULTED state and recent error posture.
   - `storage_scrub_receipt_digests` are the typed join for exact scrub / repair outcomes.
   - This ADR does not add a new generic field for raw `zpool status`, SMART dumps, dashboard screenshots, or whole scrub transcripts.

4. **Use the receipt join only when integrity verification materially shaped the story.**
   - Bundles should include `storage_scrub_receipt_digests` when a scrub, a repaired corruption event, or a failed/partial integrity-verification outcome materially participated in the incident/support story.
   - Bundles do not need to include every historical `storage.scrub.receipt`.

5. **Do not promote ad-hoc CLI output or dashboards into official handoff truth.**
   - This ADR does not bless `zpool status` transcripts, SMART dashboards, or ticket prose as the canonical support-handoff proof.
   - Those remain auxiliary or stronger side-evidence lanes under explicit export policy.

## Consequences

- The official support handoff now stays aligned with the already-decided storage-integrity evidence posture instead of partially undoing it.
- Support, fleet, and audit flows can distinguish “what pools existed,” “what state the host believed now,” and “what exact verification action happened” without leaving the bundle contract.
- Canonical examples become mechanically checkable instead of placeholder-shaped for the storage lane too.
- The archive keeps a narrow boundary: no new subsystem, no generic storage-debug blob, and no automatic promotion of CLI transcripts into routine support truth.

## Alternatives considered

- **Rely on `storage_health_snapshot_digest` alone.** Rejected: current health state is not the same as the exact verification / repair proof when a scrub or repair outcome shaped the incident.
- **Add a generic `storage_status_output_digests` field to `incident.bundle`.** Rejected for now: the archive already has typed inventory/snapshot/receipt surfaces for normal support handoff, and a broader transcript field would widen the routine contract before it is needed.
- **Let `zpool status` output or dashboards tell the story.** Rejected: that recreates implementation-private folklore and weakens portability / explainability across product shapes.

## Status

Accepted and wired through the bundle examples, support-bundle docs, curated storage references, and archive hygiene checks.
