# Filled rematch-world benchmarks should carry one copy-forward audit receipt

A filled rematch-world benchmark artifact should not merely *look* like it preserved the copied handoffs from the standing seed.
It should carry one tiny receipt proving that those copied sections actually survived unchanged into the publication artifact.

## Why this matters

The archive now has a layered handoff chain:

1. the frozen seed audit proves the standing seed still matches its standalone copied handoff sources,
2. the compiled publication artifact should then prove it preserved those copied sections while filling only the world-dependent fields.

Without the second step, an inheritor must trust that a large compiled artifact still carries the same copied interpretation and decision surfaces that were frozen in the seed.

## What to keep

Keep one small copy-forward audit receipt that checks:

- the seven copied handoff sections still match the standing seed exactly, and
- the compact decision bundle still matches the standing decision contract exactly.

That receipt can cite the frozen seed audit for the standalone provenance chain instead of duplicating every source digest again.

## Operational rule

Run the copy-forward audit after the compiled artifact exists and before the retained publication bundle is treated as the final handoff surface.
If it fails, rebuild from the standing seed or compact patch instead of repairing the copied handoffs by hand inside the compiled artifact.
