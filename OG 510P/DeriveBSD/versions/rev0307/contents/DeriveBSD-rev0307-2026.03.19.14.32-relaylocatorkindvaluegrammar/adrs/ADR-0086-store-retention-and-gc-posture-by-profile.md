# ADR-0086: Store retention and GC posture by profile

Date: 2026-03-07
Status: Accepted

## Context

DeriveBSD already has the raw ingredients for a coherent retention lane:
`docs/175-pins-roots-and-garbage-collection.md`, `docs/404-zfs-boot-environments-as-system-generations.md`, and `docs/426-store-gc-plans-and-receipts.md`
cover explicit roots/pins, ZFS boot environments, and receipted garbage collection.

What the archive still lacked was a **product-default boundary** for how those pieces behave in each product shape.
Without that boundary, “GC” drifts into contradictory expectations:

- fleet hosts either preserve a hard rollback floor or quietly garbage-collect their way out of a safe recovery window,
- workstations either make cleanup visible and humane or silently delete the user’s obvious rollback points under disk pressure,
- general-purpose systems cannot tell whether aggressive cleanup is an explicit local-admin act or hidden background policy,
- and factory/regulatory images either retain approved rollback and audit windows or claim traceability while pruning the very artifacts they need later.

The existing `store.gc.plan` model also had one important ambiguity:
`keep_generations` looked like both a convenience preference and a hard safety floor.
Those are not the same thing.

## Decision

DeriveBSD will treat **store retention / GC posture** as a first-class, profile-shaped default captured in
`spec/examples/product.profiles.json` under `store_retention` and guarded by `tools/check_product_profiles.py`.

The default values are:

- **A / `fleet_host`**: `rollback-floor-policy-gated`
- **B / `workstation`**: `trusted-ui-visible-space-pressure-rollback-floor`
- **C / `general_os`**: `pins-and-generations-explicit-admin`
- **D / `appliance_factory`**: `offline-auditable-rollback-floor`

DeriveBSD also tightens the GC artifacts themselves:

1. `store.gc.plan.constraints.keep_generations` remains a **retention preference**.
   It is a bias toward keeping at least N generations when space allows.

2. `store.gc.plan.constraints.rollback_floor_generations` is a separate **hard safety floor** for bootable system rollback coverage.
   For host/system scopes, apply-mode plans should not reduce healthy bootable generations below this floor without an explicit stronger lane.

3. `store.gc.receipt.rollback_coverage` records whether that floor was preserved after the run.
   This makes “did GC shrink rollback coverage?” a one-object answer instead of a forensic reconstruction exercise.

4. Pins, active boot entries, boot-try windows, and incident/audit holds remain independent liveness roots.
   GC policy may prefer reclaiming bytes, but it does not get to redefine liveness by accident.

## Meaning by profile

### A) Secure fleet host (`fleet_host`)

- GC must preserve a hard bootable rollback floor as the normal case.
- Dry-run plans, policy promotion, and bounded deletion volume are the expected operational path.
- Disk pressure does not justify silently erasing cohort rollback safety.

### B) Secure workstation (`workstation`)

- Cleanup can be ergonomic, but it must stay visible in trusted UI when it threatens obvious rollback points.
- Explicit pins and recent user-visible generations should survive ordinary space-pressure cleanup.
- Stronger reclamation remains an explicit reviewed choice, not a background surprise.

### C) General-purpose OS (`general_os`)

- Roots/pins/generations remain explicit and queryable.
- More aggressive cleanup is a viable local-admin action, but it must stay explicit rather than hidden folklore.
- Compatibility lanes do not get to hide retention semantics from the operator.

### D) Appliance factory / regulatory (`appliance_factory`)

- Production GC must preserve approved rollback and audit windows.
- Retention changes belong in maintenance/offline workflows with receipts, not ad-hoc disk-pressure scripts.
- Evidence needed for support, audit, or regulated rollback should not disappear silently.

## Consequences

### Positive

- The archive now distinguishes between “prefer to keep more” and “must not cross this rollback floor”.
- A/B/C/D get a stable answer to what GC is allowed to optimize away by default.
- GC receipts can now answer whether rollback coverage survived, not just how many bytes were reclaimed.

### Negative / trade-offs

- This adds one more stable profile knob that must stay small and guardrailed.
- Exact floor numbers, deletion scheduling, and UI polish remain implementation work.
- Some deployments will need explicit capacity planning instead of hoping GC can paper over undersized disks.

## Non-goals

This ADR does **not** decide:

- the exact numeric rollback floor for every host class,
- the final trusted-UI cleanup UX on workstations,
- the exact cohort math for fleet-wide rollback budgets,
- or the exact archival budget for every regulated evidence class.

Those remain implementation work or future RFC/ADR material.

## Why this shape

The coherence win is not “never garbage collect” and it is not “reclaim bytes at any cost.”
It is deciding that:

- A defaults to a policy-gated rollback floor,
- B defaults to trusted-UI-visible cleanup under space pressure with rollback protection,
- C defaults to explicit pins/generations semantics with local-admin viability,
- D defaults to offline/auditable rollback-floor preservation.

That is enough to guide future specs and coding without prematurely freezing every retention number or cleanup daemon.
