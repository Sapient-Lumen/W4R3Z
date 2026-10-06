# RFC-0162: Time discipline + trustworthy timestamps as evidence

Status: Draft  
Last updated: 2026-02-24

## Motivation

DeriveBSD is building an ops spine where facts are typed and reusable:
health gates, change receipts, incident bundles, attestation receipts, secret grants.
All of these implicitly depend on **time**.

If time is wrong or untrusted, we get:
- broken correlation (“which change caused this?”)
- ambiguous incident timelines
- posture/attestation and secret release policies that are easy to bypass via time skew
- operational outages caused by surprise clock steps

Most OSes treat time sync as best-effort configuration and string logs.
DeriveBSD should treat it as a first-class evidence lane.

## Proposal

Introduce these new evidence objects:

1) **`time-source-inventory`**
   - privacy-safe description of time sources available on a host (NTP/NTS/PTP/RTC/optional sources)

2) **`time-sync-plan`**
   - explicit plan describing how the host disciplines time (sources, auth mode, step/slew policy)

3) **`time-sync-snapshot`**
   - compact “time health” snapshot: sync state, offset/uncertainty bounds, reference source, last sync

4) **`time-sync-receipt`**
   - append-only evidence for time actions: step/slew/source-change/leap handling

5) **`time-requirement`**
   - small policy-shaped gate object (max offset, freshness, require authenticated sources, step limits)

6) **`time-event`**
   - typed structured journal event stream for time milestones and clock steps

### Change set integration

Add a new change-set step op:
- `op: require-time-sync`
- references one `time-requirement` object

### Health gate integration

Update health-gated updates to optionally include:
- a `time-sync-snapshot` gate (fresh, within bounds)

### Incident bundle integration

Extend incident bundles to optionally include:
- `time-source-inventory` digest
- `time-sync-snapshot` digest
- recent `time-sync-receipt` digests

## Design notes

- Keep it optional: hosts may run without NTS/PTP, but higher-assurance workflows can require it.
- Treat clock steps as a first-class operational event (receipt + event).
- Prefer metadata-first objects; avoid embedding server addresses by default (allow hashing/redaction).

## Open questions

- Do we need a standardized “quorum” vocabulary (e.g., N-of-M sources within skew), or keep it policy-specific for v1?
- Do we want to standardize a “time bootstrap” evidence object (Roughtime quorum decision) or treat it as an implementation detail of `time-sync-receipt`?

## Schema references

- `spec/time.source.inventory.schema.json`
- `spec/time.sync.plan.schema.json`
- `spec/time.sync.snapshot.schema.json`
- `spec/time.sync.receipt.schema.json`
- `spec/time.requirement.schema.json`
- `spec/time.event.schema.json`
