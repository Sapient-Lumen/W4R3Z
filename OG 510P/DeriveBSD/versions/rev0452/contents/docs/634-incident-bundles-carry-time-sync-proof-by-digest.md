# Incident bundles carry time-sync proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility, supply-chain  
**Patterns:** Plan→Apply→Receipt, Bundles  

DeriveBSD already decided that trustworthy time should be typed and explainable.
This doc fixes the smaller but implementation-shaping support/export question the archive still left fuzzy in practice:

**how does the official incident/support bundle contract name the exact `time.sync.receipt` when clock steps, source failover, or degraded trustworthy time actually shaped the story?**

The answer is intentionally narrow.
It is not a new time subsystem and not a generic transcript blob.
It is the missing decision to make the existing time-discipline artifacts joinable through the official support-handoff contract.

See also:
- ADR: `adrs/ADR-0224-incident-bundles-carry-time-sync-proof-by-digest.md`
- time lane: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`
- backend notes: `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`
- monitor lane: `docs/308-time-monitors-and-lie-detection.md`
- profile posture: `docs/468-trustworthy-time-posture-by-profile.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`

## Why this needs a hard decision

`docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md` already made the trustworthy-time lane explicit:

- `time-source-inventory` describes what sources exist,
- `time-sync-snapshot` is the compact current health surface,
- `time-sync-receipt` is the authoritative proof of steps, source changes, and convergence actions,
- and `time-proof-bundle` remains the richer transcript-derived evidence object.

But the official support/export contract still lagged behind that design in practice.
`incident.bundle` could already carry `time_source_inventory_digest`, `time_sync_snapshot_digest`, and `time_sync_receipt_digests`, but the archive still did not explicitly teach that support handoff should use those typed joins when trustworthy-time actions materially shaped the incident.

A coherent archive should let support bundles answer all three questions distinctly:

- **what time sources were available?**
- **what sync state did the host believe at handoff time?**
- **what exact bounded time-discipline action happened?**

## Accepted boundary

### 1) Bundles may carry exact time-discipline action proof

Support bundles should not force readers to infer clock correction or source failover from daemon-private output.

- `time_sync_receipt_digests` name the exact `time.sync.receipt` objects that belong to the incident.
- The referenced `time.sync.receipt` objects remain the place that points at the plan digest, before/after snapshot digests, and the action performed.

That keeps the official support contract compact while still naming the canonical action proof.

### 2) The official selectors are now treated as real

The canonical include surface already carries `time_source_inventory`, `time_sync_snapshot`, and `time_sync_receipts`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same typed selectors apply both when planning a support bundle and when recording what the final bundle included.

That keeps trustworthy-time context on the official support-bundle lane instead of buried in `extra`, daemon logs, monitor dashboards, or ticket prose.

### 3) Keep inventory, current state, and exact action proof separate

This is the design cut worth preserving.
The archive does **not** collapse all trustworthy-time evidence into one generic field.

- `time_source_inventory_digest` is the typed join for source posture.
- `time_sync_snapshot_digest` is the typed join for current sync/degraded/unsynced state.
- `time_sync_receipt_digests` are the typed join for exact clock steps, source changes, or convergence actions.
- `time-proof-bundle` remains richer side evidence for protocol/agreement analysis.

That keeps “what sources existed,” “what the host currently believed,” and “what exact corrective action happened” separately explainable.

### 4) Include receipt proof when it materially shaped the story

The rule is intentionally conditional.
The archive does **not** require every incident bundle to include every historical `time.sync.receipt`.
Instead, bundles should carry `time_sync_receipt_digests` when trustworthy-time actions materially participated in or shaped the incident/support story.

Examples:

- a fleet incident needs to prove the exact clock-step or source-change action that made certificate-expiry verification fail closed,
- a workstation support case needs to show the one bounded time correction that explains why local UI and server-side timestamps disagreed,
- a general-purpose install needs to tie a broken update or secret-fetch flow to one explicit degraded-time recovery instead of a support engineer reconstructing it from daemon logs,
- or an appliance/factory handoff needs to prove what exact time convergence action happened during an offline/bootstrap window.

### 5) Raw transcripts and daemon logs remain stronger side evidence

This boundary does not promote chrony/ntpd/NTPsec logs, monitor dashboards, or raw NTS/Roughtime transcripts into the official bundle truth model.
Put differently: keep daemon logs, monitor dashboards, or raw NTS/Roughtime transcripts out of the routine support-handoff truth surface.
Those aids may still exist as auxiliary review material, but the default support-handoff joins stay digest-first:

- exact `time-source-inventory` digest,
- exact `time-sync-snapshot` digest,
- exact `time.sync.receipt` digests when an action mattered,
- and richer transcript-derived proof only through explicit stronger export paths.

That keeps backend-private diagnostics and official support/export truth separate.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove which exact time-discipline action participated in an expiry-sensitive failure or degraded-quorum investigation instead of normalizing daemon logs or monitor dashboards as the official evidence.

### B / secure workstation

Workstation support handoff can now export one exact `time.sync.receipt` when the user or support flow needs to explain a visible clock correction, instead of making support infer it from screenshots or prose.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed trustworthy-time story explicit in bundles without pretending every foreign time daemon or manual fix inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes can now answer what exact bounded trustworthy-time action shaped the incident handoff without collapsing the story into raw transcripts, dashboards, or ticket notes.

## Guardrail

- `tools/check_time_sync_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces keep time-discipline proof explicit, that the canonical bundle example binds the real `time.source.inventory`, `time.sync.snapshot`, and `time.sync.receipt` example digests, and that the relevant docs keep teaching the same trustworthy-time/support-bundle story.

## What remains open

This doc does **not** fix:

- the exact UI for previewing trustworthy-time evidence before export,
- whether every bundle template enables the time selectors by default,
- whether future support handoffs should carry more than one `time.sync.receipt`,
- or broader support-handoff joins for `time-proof-bundle` transcript evidence.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention clock correction or time failover only in prose while hand-waving the exact `time.sync.receipt` action proof.

Last updated: 2026-03-21r364
