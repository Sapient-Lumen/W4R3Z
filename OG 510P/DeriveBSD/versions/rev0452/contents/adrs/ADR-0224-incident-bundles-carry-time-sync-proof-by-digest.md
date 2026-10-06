# ADR-0224: Incident bundles carry time-sync proof by digest

Date: 2026-03-21
Status: Accepted

## Context

`docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`, `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`, `docs/308-time-monitors-and-lie-detection.md`, and `docs/468-trustworthy-time-posture-by-profile.md` already fixed the core trustworthy-time lane:

- `time-source-inventory` describes what sources exist,
- `time-sync-snapshot` is the compact current health surface,
- `time-sync-receipt` is the authoritative proof of clock steps, source changes, and convergence actions,
- and `time-proof-bundle` remains the richer transcript-derived evidence object when deeper time-source agreement analysis is needed.

The official incident/support-bundle contract still lagged behind that decision in practice.
`incident.bundle` already had selectors and fields for `time_source_inventory_digest`, `time_sync_snapshot_digest`, and `time_sync_receipt_digests`, but the archive still did not treat the exact `time.sync.receipt` as official support-handoff proof when clock correction, source failover, or degraded trustworthy time materially shaped an incident.
The canonical examples did not bind the real time digests, and the surrounding docs still made it too easy to retell time problems through daemon logs, monitor dashboards, or raw protocol transcripts.

That omission is expensive because it blurs three distinct questions:

- what time sources were available on the host,
- what current sync state the host believed at handoff time,
- and what exact bounded time-discipline action happened.

Without an explicit join, responders drift back toward daemon-private status output, protocol transcripts, or ticket prose just to answer whether the clock actually stepped, lost quorum, or changed sources.

## Decision

**Incident/support bundles may carry time-discipline proof by typed digest joins.**

1. **Treat the existing time selectors and metadata fields as official support-handoff surfaces.**
   - `time_source_inventory` / `time_source_inventory_digest` identify the bounded source inventory relevant to the incident.
   - `time_sync_snapshot` / `time_sync_snapshot_digest` identify the compact current trustworthy-time state.
   - `time_sync_receipts` / `time_sync_receipt_digests` identify the exact `time.sync.receipt` objects when steps, source changes, or convergence failures materially shaped the incident/support story.

2. **Make the shared bundle-plan include surface real for time as well.**
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` already carries `time_source_inventory`, `time_sync_snapshot`, and `time_sync_receipts`.
   - `bundle.plan.selection.include` must exercise those selectors when support handoff needs trustworthy-time inventory, current state, and exact time-discipline proof instead of retelling the story from logs.

3. **Keep inventory, current state, and exact action proof distinct inside support handoff.**
   - `time_source_inventory_digest` is the typed join for available source posture.
   - `time_sync_snapshot_digest` is the typed join for current sync/degraded/unsynced state.
   - `time_sync_receipt_digests` are the typed join for exact clock-discipline actions.
   - `time-proof-bundle` remains richer side evidence for deeper protocol/agreement investigation; this ADR does not add a new generic bundle field for raw transcripts or proof-bundle blobs.

4. **Use the receipt join only when trustworthy-time actions materially shaped the story.**
   - Bundles should include `time_sync_receipt_digests` when clock steps, source failover, degraded quorum, or recovery from bad time materially participated in the incident/support story.
   - Bundles do not need to include every historical `time.sync.receipt`.

5. **Do not promote backend-private logs or raw transcripts into official handoff truth.**
   - This ADR does not bless chrony/ntpd/NTPsec logs, monitoring dashboards, or raw NTS/Roughtime transcripts as the canonical support-handoff proof.
   - Those remain auxiliary or stronger side-evidence lanes under explicit export policy.

## Consequences

- The official support handoff now stays aligned with the already-decided trustworthy-time evidence posture instead of partially undoing it.
- Support, fleet, and audit flows can distinguish “what sources existed,” “what state the host believed now,” and “what exact time action happened” without leaving the bundle contract.
- Canonical examples become mechanically checkable instead of placeholder-shaped for the time lane too.
- The archive keeps a narrow boundary: no new subsystem, no generic time-debug blob, no automatic promotion of raw protocol transcripts into routine support truth.

## Alternatives considered

- **Rely on `time_sync_snapshot_digest` alone.** Rejected: current state is not the same as the exact action proof when a step, source change, or degraded sync event shaped the incident.
- **Add a generic `time_proof_bundle_digests` field to `incident.bundle`.** Rejected for now: the archive already has typed inventory/snapshot/receipt surfaces for normal support handoff, and adding a broader transcript-derived field would widen the routine contract before it is needed.
- **Let daemon logs or monitor dashboards tell the story.** Rejected: that recreates implementation-private folklore and weakens portability/explainability across product shapes.

## Status

Accepted and wired through the bundle schema examples, support-bundle docs, and archive hygiene checks.
