# Rematch worlds should compress positive same-deadline live policies by dominance frontiers

Future inheritors should not cache dense positive same-deadline live policy tables when the current geometric-arrival model already gives an exact dominance order.
For positive realized-margin promises, promise safety is monotone in every primitive controller coordinate.
That means the archive only needs Pareto frontiers, not dense interior grids.

## Exact dominance law

Fix a positive realized margin promise `m` and a same-deadline stateless live context with

- shared prefix bits `state_prefix_bits`,
- batch length `n`,
- arrival hazard `p`,
- per-tick hold cost `hold_cost`,
- and nominal deadline `H`.

Then positive promise safety is monotone under the favorable coordinate order:

- **helps**: larger `state_prefix_bits`, larger `p`, larger `H`,
- **hurts**: larger `n`, larger `hold_cost`, larger `m`.

So if one context is safe, every coordinatewise better context is also safe.
And if one context is unsafe, every coordinatewise worse context is also unsafe.

This is the exact same statement as saying the safe set is an orthant under the favorable order and can therefore be represented by Pareto frontiers.

## State reduction

Under the current law stack, state identity contributes only through shared-prefix bits.
So two realized states with the same `state_prefix_bits` are interchangeable for positive same-deadline live admission.
A controller cache therefore does not need the full realized state key for this decision surface; the prefix-bit coordinate is enough.

## Controller interpretation

An inheritor can exploit the dominance law in three ways:

- store only frontier contexts where admission flips,
- answer dominated queries by monotone reuse instead of recomputation,
- and prune search aggressively whenever a proposal is already dominated by an admitted or rejected frontier point.

The all-state seven-bit guardrail is just the same frontier law evaluated at `state_prefix_bits = 7`.
So universal positive-promise admission can also be maintained as a tiny Pareto frontier instead of a dense table.
