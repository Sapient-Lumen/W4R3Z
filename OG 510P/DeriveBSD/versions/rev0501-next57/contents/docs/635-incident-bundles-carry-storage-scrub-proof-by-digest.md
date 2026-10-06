# Incident bundles carry storage-scrub proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility, isolation  
**Patterns:** Plan→Apply→Receipt, Bundles  

DeriveBSD already decided that storage integrity should be typed and explainable.
This doc fixes the smaller but implementation-shaping support/export question the archive still left fuzzy in practice:

**how does the official incident/support bundle contract name the exact `storage.scrub.receipt` when integrity verification, repaired corruption, or degraded storage health actually shaped the story?**

The answer is intentionally narrow.
It is not a new storage subsystem and not a generic status transcript blob.
It is the missing decision to make the existing storage-integrity artifacts joinable through the official support-handoff contract.

See also:
- ADR: `adrs/ADR-0225-incident-bundles-carry-storage-scrub-proof-by-digest.md`
- storage lane: `docs/225-storage-health-and-scrubbing-as-evidence.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- bundle plans: `docs/253-bundle-plans-and-deterministic-exports.md`
- evidence spine: `docs/229-evidence-spine-overview.md`

## Why this needs a hard decision

`docs/225-storage-health-and-scrubbing-as-evidence.md` already made the storage-integrity lane explicit:

- `storage-pool-inventory` describes bounded pool topology and feature posture,
- `storage-health-snapshot` is the compact current health surface,
- `storage-scrub-receipt` is the authoritative proof of a bounded integrity-verification run,
- and typed `storage-event` records keep scrub/resilver/degrade milestones joined to the structured journal.

But the official support/export contract still lagged behind that design in practice.
`incident.bundle` could already carry `storage_pool_inventory_digest`, `storage_health_snapshot_digest`, and `storage_scrub_receipt_digests`, but the archive still did not explicitly teach that support handoff should use those typed joins when integrity verification or repair materially shaped the incident.

A coherent archive should let support bundles answer all three questions distinctly:

- **what pool topology and feature posture existed?**
- **what health state did the host believe at handoff time?**
- **what exact bounded integrity-verification action happened?**

## Accepted boundary

### 1) Bundles may carry exact storage-integrity action proof

Support bundles should not force readers to infer scrub or repair outcomes from `zpool status` transcripts, dashboard screenshots, or operator notes.

- `storage_scrub_receipt_digests` name the exact `storage.scrub.receipt` objects that belong to the incident.
- The referenced `storage.scrub.receipt` objects remain the place that points at the plan digest, the pool inventory / health state it verified, and the outcome per pool.

That keeps the official support contract compact while still naming the canonical integrity-verification proof.

### 2) The official selectors are now treated as real

The canonical include surface already carries `storage_pool_inventory`, `storage_health_snapshot`, and `storage_scrub_receipts`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same typed selectors apply both when planning a support bundle and when recording what the final bundle included.

That keeps storage-integrity context on the official support-bundle lane instead of buried in `extra`, `zpool status` output, or ticket prose.

### 3) Keep inventory, current state, and exact verification proof separate

This is the design cut worth preserving.
The archive does **not** collapse all storage evidence into one generic field.

- `storage_pool_inventory_digest` is the typed join for pool topology / feature posture.
- `storage_health_snapshot_digest` is the typed join for current ONLINE/DEGRADED/FAULTED state and recent error posture.
- `storage_scrub_receipt_digests` are the typed join for exact scrub / repair outcomes.

That keeps “what storage existed,” “what the host currently believed,” and “what exact integrity-verification action happened” separately explainable.

### 4) Include receipt proof when it materially shaped the story

The rule is intentionally conditional.
The archive does **not** require every incident bundle to include every historical `storage.scrub.receipt`.
Instead, bundles should carry `storage_scrub_receipt_digests` when integrity verification or repair materially participated in or shaped the incident/support story.

Examples:

- a fleet incident needs to prove the exact scrub receipt that repaired checksum damage before a rollout could safely continue,
- a workstation support case needs to show the one bounded scrub result that explains a newly visible degraded-pool warning,
- a general-purpose install needs to tie repeated service failures to one explicit partial scrub or new checksum-error discovery instead of a support engineer reconstructing it from shell history,
- or an appliance/factory handoff needs to prove what exact integrity-verification run happened before a regulatory export or field replacement decision.

### 5) Raw status output remains stronger side evidence

This boundary does not promote raw `zpool status` output, SMART dashboards, or ticket prose into the official bundle truth model.
Put differently: keep `zpool status` transcripts, dashboard screenshots, and shell notes out of the routine support-handoff truth surface.
Those aids may still exist as auxiliary review material, but the default support-handoff joins stay digest-first:

- exact `storage-pool-inventory` digest,
- exact `storage-health-snapshot` digest,
- exact `storage.scrub.receipt` digests when an integrity-verification action mattered.

That keeps operator aids and official support/export truth separate.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove which exact storage-integrity action participated in rollout blocking or post-fault recovery instead of normalizing shell output or dashboard snapshots as the official evidence.

### B / secure workstation

Workstation support handoff can now export one exact `storage.scrub.receipt` when the user or support flow needs to explain a degraded-pool or repaired-corruption warning instead of making support infer it from screenshots or prose.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed storage-integrity story explicit in bundles without pretending every foreign storage tool or manual `zpool scrub` workflow inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes can now answer what exact bounded integrity-verification action shaped the incident handoff without collapsing the story into shell transcripts, dashboards, or ticket notes.

## Guardrail

- `tools/check_storage_scrub_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces keep storage-integrity proof explicit, that the canonical bundle example binds the real `storage.pool.inventory`, `storage.health.snapshot`, and `storage.scrub.receipt` example digests, and that the relevant docs keep teaching the same storage/support-bundle story.

## What remains open

This doc does **not** fix:

- the exact UI for previewing storage-integrity evidence before export,
- whether every bundle template enables the storage selectors by default,
- whether future support handoffs should carry more than one `storage.scrub.receipt`,
- or broader support-handoff joins for richer disk-vendor diagnostics.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention scrub/repair outcomes only in prose while hand-waving the exact `storage.scrub.receipt` action proof.

Last updated: 2026-03-21r365
