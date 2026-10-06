# Store GC plans and receipts (retention as evidence)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate

GC is inevitable. What matters is whether it is **predictable and explainable**.

DeriveBSD already adopts the Nix lesson that **liveness is explicit** (roots/pins define reachability).
This doc adds the missing operational piece: make GC itself a **typed, reviewable, receipted** operation.

- Plan: `store.gc.plan` (what we intend to delete, and why)
- Receipt: `store.gc.receipt` (what happened)

This keeps retention policy compatible with all product shapes (A–D) without forks:
profiles choose defaults (how many generations to keep, how aggressive GC is), but the evidence objects are uniform.

## Pattern mapping

- **Plan → Apply → Receipt:** GC runs are explicit plans (dry-run by default) that produce receipts.
- **Registry → Diff → Gate:** retention policy is a diff surface (e.g. min-free budget, keep-generations); policies can gate “dangerous” plans (large deletions, deleting too-new generations).

## Why GC is evidence

Without receipts, GC becomes a common incident failure mode:
- a fleet silently falls out of rollback coverage,
- a workstation loses the ability to reproduce a past build,
- an appliance can’t produce required forensic bundles because evidence was pruned.

A `store.gc.receipt` is a compact, queryable answer to:
- *what did we delete?*
- *why was it eligible?*
- *what roots/pins prevented deletion?*
- *did we preserve rollback windows?*

## The GC plan object

Schema: `spec/store.gc.plan.schema.json`
Example: `spec/examples/store.gc.plan.json`

A `store.gc.plan` is deliberately a **stable review surface**, not a full GC algorithm.
It binds:
- **scope** (which store namespace / kinds)
- **root set** (what defines liveness)
- **constraints** (dry-run vs apply; caps/budgets)
- **candidate list** (what would be deleted + reason)

Recommended discipline:

1) Default to **dry-run** plans
   - require an explicit promote step (policy or operator) to switch `constraints.mode` to `apply`.

2) Treat retention knobs as policy
   - `keep_generations` is a baseline safety rail; profiles can raise it for fleets/regulatory.

3) Keep GC bounded
   - cap deletion volume (`max_delete_bytes`) and prefer incremental, frequent GC over rare, massive runs.

## The GC receipt object

Schema: `spec/store.gc.receipt.schema.json`
Example: `spec/examples/store.gc.receipt.json`

A `store.gc.receipt` is a compact result summary bound to `plan_digest`.
It records outcome, aggregate stats, and (optionally) a truncated list of deletions/retentions.

Operational rule: if a run deletes *a lot*, export a full deletion list as a separate evidence object and reference it by digest.
(Keep the receipt itself small so it stays easy to ship in incident bundles.)

## Wiring into existing GC semantics

This doc does not replace the existing roots/pins model; it **makes it visible**.

- GC semantics and roots/pins: `docs/175-pins-roots-and-garbage-collection.md`
- ZFS BE retention and rollback windows: `docs/404-zfs-boot-environments-as-system-generations.md`

References (prior art):
- Nix manual — garbage collection: https://nix.dev/manual/nix/2.26/package-management/garbage-collection
- Nix Pills — the garbage collector: https://nixos.org/guides/nix-pills/11-garbage-collector.html

## Minimal v0 wiring

- `derive gc plan` emits `store.gc.plan` (dry-run)
- `derive gc apply` requires policy approval and emits `store.gc.receipt`
- The latest receipt digest is discoverable via the evidence query surface (so “when did GC last run?” is one query)

