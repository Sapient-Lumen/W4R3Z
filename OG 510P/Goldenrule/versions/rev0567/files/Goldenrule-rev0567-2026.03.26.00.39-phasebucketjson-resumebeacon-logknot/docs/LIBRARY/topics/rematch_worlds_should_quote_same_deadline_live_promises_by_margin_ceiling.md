# Rematch worlds should quote same-deadline live promises by margin ceiling

Future inheritors should not pick same-deadline stateless live promise levels by trial-and-error against timeout or batch tables.
Under the current geometric-arrival model, the largest nonnegative realized margin promise is available in one closed form.

## Exact live margin ceiling law

Let:
- `H` be the nominal deadline of a stateless live controller that re-checks after every miss,
- `n` be the current batch length,
- `p` be the per-tick arrival hazard,
- `hold_cost` be the per-tick waiting cost,
- and `state_prefix_bits` be the current shared-state gain numerator.

Then same-deadline stateless live control can preserve original realized margin promises exactly up to

`max(0, (1 - (1 - p)^floor((H + 1) / 2)) * (state_prefix_bits / (n(n + 1)) - hold_cost / p))`.

Equivalently, the controller may safely quote any nonnegative realized margin promise `m` with

`m <= max(0, (1 - (1 - p)^floor((H + 1) / 2)) * (state_prefix_bits / (n(n + 1)) - hold_cost / p))`.

This is exactly the better of:
- immediate close now, and
- blind commit with effective horizon `floor((H + 1) / 2)`.

## Practical interpretation

This gives the inheritor a one-line promise-quoting rule:
1. reduce nominal live deadline `H` to effective blind horizon `floor((H + 1) / 2)`,
2. compute the closed-form nonnegative margin ceiling above,
3. and never quote a same-deadline live realized-margin promise above that ceiling.

Equivalent consequences:
- if the raw effective blind value is positive, that value is the exact maximum quoteable realized margin,
- if the raw effective blind value is zero or negative, only the zero-margin promise survives,
- and every strictly larger promise fails immediately.

## Odd/even deadline ladder

Because the ceiling depends only on `floor((H + 1) / 2)`, deadlines `2j - 1` and `2j` have the same nonnegative live margin ceiling.
Promise-quoting capacity only improves when the nominal deadline climbs to the next odd rung.
So the same odd/even pairing that governed minimum deadlines, batch caps, and hold-cost ceilings also governs maximum quoteable realized margin.

## Zero-only regime

When the raw effective blind value is nonpositive, the controller is still nonnegatively safe because it can close immediately.
But that means the ceiling collapses to exactly `0`: there is no positive realized-margin promise left to quote under same-deadline live control.

## All-state guardrail

The same law holds under the seven-bit all-state lower envelope after replacing `state_prefix_bits` by `7`.
So a universal same-deadline stateless live controller can also quote promises from one closed-form nonnegative margin ceiling.
