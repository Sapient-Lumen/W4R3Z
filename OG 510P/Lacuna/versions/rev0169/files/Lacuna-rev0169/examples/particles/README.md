# Particle-bank examples

This directory demonstrates the two review-first particle operations:

- `update.template.json` applies one new evidence factor over the complete eligible population.
- `reconcile.template.json` replays the current factor epoch from its immutable baseline after factor authority changes.

## Apply a factor

Request the current complete-bank receipt:

```bash
./lacuna particle-update-review CUBE ast.red-dust
```

Replace the IDs and digest in `update.template.json`, then submit it through `./lacuna apply CUBE FILE`, direct `Cube.apply_changeset`, or an unscoped director turn.

The vector must cover every `live` or `selected` world exactly once. The operation changes weights only. It does not select, prune, merge, resample, or canonize a world.

## Reconcile withdrawn factors

After an applied evidence assertion is superseded, inspect debt and request a deterministic replay review:

```bash
./lacuna particle-bank CUBE
./lacuna particle-reconciliation-review CUBE
```

Copy the current head and `expected_reconciliation_sha256` into `reconcile.template.json`, then apply it. The operation reconstructs the epoch baseline from the first update's immutable prior receipt, includes every still-active factor, excludes ended factors without deleting them, and computes the resulting distribution in log space.

Inspect custody with:

```bash
./lacuna particle-reconciliations CUBE
./lacuna verify CUBE
```

Reconciliation is a complete-population planner operation. It is available to host/direct Python and unscoped director turns, but not to audience or world-scoped contexts.
