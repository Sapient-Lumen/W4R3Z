# Store retention and GC posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility, supply-chain  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD already has serious retention primitives.
What this doc decides is narrower and more important for coherence:
**what is the default store-retention / GC posture in each product shape?**

This is intentionally **not** a GC daemon or storage-sizing spec.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0086-store-retention-and-gc-posture-by-profile.md`
- roots and pins: `docs/175-pins-roots-and-garbage-collection.md`
- ZFS boot environments: `docs/404-zfs-boot-environments-as-system-generations.md`
- GC plan/receipt artifacts: `docs/426-store-gc-plans-and-receipts.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Every derivation-first system that avoids deciding retention posture eventually decides it through drift:

- fleet hosts quietly prune known-good rollback generations because disk pressure always feels urgent,
- workstations hide cleanup in background jobs until the human discovers the one version they needed is gone,
- general-purpose systems cannot tell whether aggressive GC is a legitimate local-admin action or a bug,
- and factory/regulatory images claim long-term traceability while silently deleting the receipts and bootable states that made the claim credible.

DeriveBSD already says liveness should be explicit and GC should be receipted.
That only becomes coherent if the archive fixes the **default authority model for retention pressure vs rollback coverage** instead of leaving it to whichever cron job or cleanup helper appears first.

## Product-shape defaults

| Profile | `store_retention` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `rollback-floor-policy-gated` | Fleet GC preserves a hard bootable rollback floor by default; apply-mode cleanup is dry-run-first, policy-shaped, and bounded instead of disk-pressure panic. |
| B (`workstation`) | `trusted-ui-visible-space-pressure-rollback-floor` | Cleanup can react to local disk pressure, but obvious rollback points and pins remain protected unless the human reviews a stronger cleanup in trusted UI. |
| C (`general_os`) | `pins-and-generations-explicit-admin` | Pins and recent generations stay explicit/queryable by default; more aggressive reclamation remains a viable explicit local-admin action rather than hidden automation. |
| D (`appliance_factory`) | `offline-auditable-rollback-floor` | Production GC preserves approved rollback/audit windows and stays maintenance/offline/receipted rather than ad-hoc live cleanup folklore. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## One important contract split: preference vs floor

The archive now treats two retention knobs as distinct on purpose:

- `store.gc.plan.constraints.keep_generations` is a **preference**
  - “keep at least this many generations when practical”
- `store.gc.plan.constraints.rollback_floor_generations` is a **hard safety floor**
  - the core field token is `rollback_floor_generations`
  - “do not apply this plan if it would reduce healthy bootable rollback coverage below this point without a stronger lane”

That split matters because “keep more if possible” and “must not cross this line” are not the same policy.
Lumping them together is how systems silently GC away their recovery story.

## Cross-profile invariants

Regardless of profile:

- active roots, pins, boot-try windows, and incident/audit holds remain independent liveness inputs
- GC plans should be reviewable before deletion, with apply-mode treated as a deliberate step
- reclaimed bytes are not success if rollback coverage or auditability quietly disappears
- retention decisions should be queryable after the fact through `store.gc.receipt`, especially the `rollback_coverage` summary
- stronger cleanup lanes in C do not silently redefine stricter A/B/D defaults

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `rollback-floor-policy-gated`

- Fleet hosts should not fall out of rollback coverage because a local store filled up.
- GC stays dry-run-first, policy-approved, and deletion-volume-bounded.
- Cohort rollout policy may get stricter later, but the product default is already clear: preserve rollback floors first, reclaim space second.

### B) Secure workstation (`workstation`)

Default: `trusted-ui-visible-space-pressure-rollback-floor`

- Workstations can be humane about disk pressure, but cleanup must stay explainable to the human.
- Current/recent user-visible rollback points and explicit pins survive ordinary cleanup.
- Stronger reclamation belongs in trusted UI review rather than background deletion folklore.

### C) General-purpose OS (`general_os`)

Default: `pins-and-generations-explicit-admin`

- General-purpose systems keep roots/pins/generations legible by default.
- Aggressive cleanup remains a viable explicit local-admin action.
- This preserves compatibility and local control without hiding retention semantics.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `offline-auditable-rollback-floor`

- Regulated and factory shapes need retained rollback and evidence windows that survive routine operations.
- Production cleanup should happen in maintenance/offline paths with receipts.
- Disk pressure is real, but it does not outrank auditability or approved rollback coverage by default.

## Design cue from current systems

A few lessons are stable:

- Nix makes liveness predictable by rooting store objects explicitly instead of guessing what should survive.
- OpenZFS holds make snapshot retention non-accidental, while bookmarks preserve incremental replication continuity even after snapshots are destroyed.
- The practical failure mode is not “GC exists”; it is “GC is allowed to erase the recovery story without leaving a compact explanation behind.”

DeriveBSD should steal those lessons while keeping exact floor numbers and scheduling policy open.

Last updated: 2026-03-07r225
