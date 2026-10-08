# Rematch worlds should cap same-deadline stateless live batches by effective horizon

Future inheritors should not size a same-deadline stateless live batch against its full nominal deadline.
Under the current geometric-arrival model, that overstates the positive promise class the controller can really preserve.

## Exact positive live batch-cap law

Let `H` be the nominal deadline of a stateless live controller that re-checks after every miss.
For a **positive** realized margin floor `m > 0`, the exact admissible batch cap is the largest `n` satisfying

`n(n + 1) <= p * state_prefix_bits / (hold_cost + p * m / (1 - (1 - p)^floor((H + 1) / 2)))`.

So the inheritor can reuse the earlier fixed-timeout batch-cap law exactly by substituting the effective blind horizon

`floor((H + 1) / 2)`

for the nominal live deadline `H`.

Equivalently:
- positive live promises are capped exactly as though blind commit had only `floor((H + 1) / 2)` ticks,
- deadlines `2j - 1` and `2j` therefore have the same positive live batch cap,
- and every second nominal deadline tick is dead reserve from the standpoint of exact positive-promise preservation.

## Zero-margin edge case

At margin floor `m = 0`, the controller equivalence is broader.
Same-deadline stateless live control is as promise-safe as choosing the better of immediate close and blind commit with effective horizon `floor((H + 1) / 2)`.
Because immediate close already realizes value `0`, **every** batch length is admissible against a zero floor.

So the live batch cap is:
- finite and exact from the formula above when `m > 0`,
- but unbounded in `n` when `m = 0`.

That is not a contradiction.
It is the controller-level consequence of allowing immediate close as a valid nonnegative-floor action.

## Implementation rule

If the implementation wants exact preservation of a positive realized margin promise under same-deadline stateless live control, it should:
1. choose the nominal deadline `H`,
2. compute `floor((H + 1) / 2)`,
3. and cap admissible batch length exactly as though blind commit had only that smaller timeout.

If the floor is exactly zero, the controller does not need a positive batch-cap guardrail for promise safety alone, because immediate close is already safe.

## All-state guardrail

The same law holds under the seven-bit all-state lower envelope.
So a universal same-deadline stateless live controller should cap positive promised batch length with the same formula after replacing `state_prefix_bits` by `7`.
