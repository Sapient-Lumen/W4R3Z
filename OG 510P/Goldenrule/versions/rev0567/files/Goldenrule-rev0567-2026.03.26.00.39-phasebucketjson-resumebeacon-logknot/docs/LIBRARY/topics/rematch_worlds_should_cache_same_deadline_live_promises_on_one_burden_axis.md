# Rematch worlds should cache same-deadline live promises on one burden axis

Future inheritors should not store separate same-deadline live policy tables over both per-tick hold cost and promised realized margin.
Under the current geometric-arrival law stack, those two coordinates collapse to one exact scalar burden.
That means frontier caches and runtime admission checks can lose a whole axis without approximation.

## Exact burden law

Fix batch length `n`, arrival hazard `p`, nominal live deadline `H`, per-tick hold cost `hold_cost`, and promised realized margin `m`.
Let the effective blind horizon be

`h = floor((H + 1) / 2)`.

Then the exact same-deadline live burden is

- `b_live = 0` when `m = 0`, because immediate close is already safe,
- `b_live = hold_cost / p + m / (1 - (1 - p)^h)` when `m > 0`.

The promise is preserved exactly iff

`state_prefix_bits / (n(n + 1)) >= b_live`.

Equivalently,

`state_prefix_bits >= ceil(n(n + 1) * b_live)`.

The all-state seven-bit guarantee is the same rule with `state_prefix_bits = 7`.

## Why this matters

The burden law means that, for fixed `n`, `p`, and `H`, the controller does **not** need separate cache keys for `(hold_cost, promised_margin)`.
Any two contexts with the same burden are exact substitutes for admission.
So the archive can store frontiers over

- shared-prefix bits,
- batch length,
- arrival hazard,
- nominal deadline,
- and one burden scalar,

instead of carrying both cost and margin as independent policy axes.

## Exchange-rate view

For positive promises, hold cost and promised margin trade at one exact rate:

`delta_margin = - ((1 - (1 - p)^h) / p) * delta_hold_cost`.

So at fixed hazard and deadline, increasing hold cost by `delta_hold_cost` consumes the same admission budget as increasing promised realized margin by `((1 - (1 - p)^h) / p) * delta_hold_cost`.

## Deadline pairing survives

Because the burden uses `h = floor((H + 1) / 2)`, deadlines `2j - 1` and `2j` induce the same burden map.
So the one-axis cache only changes when the nominal live deadline climbs to the next odd rung.
