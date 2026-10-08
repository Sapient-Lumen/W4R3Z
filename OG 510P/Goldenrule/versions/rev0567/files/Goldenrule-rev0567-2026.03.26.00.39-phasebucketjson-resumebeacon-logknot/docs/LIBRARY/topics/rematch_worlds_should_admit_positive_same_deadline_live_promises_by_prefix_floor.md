# Rematch worlds should admit positive same-deadline live promises by prefix floor

Future inheritors should not decide whether a same-deadline stateless live promise is admissible by searching timeout or margin tables.
Under the current geometric-arrival model, positive promise admission reduces to one integer prefix-budget floor.

## Exact live prefix-floor law

Let:
- `H` be the nominal deadline of a stateless live controller that re-checks after every miss,
- `n` be the current batch length,
- `p` be the per-tick arrival hazard,
- `hold_cost` be the per-tick waiting cost,
- `m` be the original realized margin promise,
- and `state_prefix_bits` be the current shared-state gain numerator.

For positive realized margin floors `m > 0`, same-deadline stateless live control preserves the original promise exactly when

`state_prefix_bits >= ceil(n(n + 1) * (hold_cost / p + m / (1 - (1 - p)^floor((H + 1) / 2))))`.

So the inheritor can turn live admission into a single integer threshold test:
1. reduce nominal deadline `H` to effective blind horizon `floor((H + 1) / 2)`,
2. compute the required prefix floor above,
3. and admit the positive promise exactly when the current state meets or exceeds that floor.

## Zero-margin degenerate case

If `m = 0`, the required prefix floor is exactly `0` bits.
That is not because waiting became free; it is because immediate close is already safe, so no positive shared-prefix budget is required to preserve a zero realized-margin promise.

## Universal seven-bit guardrail

The same floor also gives the exact all-state admission rule.
A universal same-deadline live promise survives exactly when the computed required prefix floor is at most `7`.
So the state-specific admission test and the universal seven-bit guardrail are the same theorem viewed at two available prefix budgets.

## Odd/even deadline ladder

Because the floor depends only on `floor((H + 1) / 2)`, deadlines `2j - 1` and `2j` have identical positive live prefix floors.
Only the next odd rung can lower the required prefix budget.
So the same dead-reserve pairing already seen in effective-horizon, minimum-deadline, batch-cap, hold-cost, and margin-ceiling laws also appears in direct prefix admission.

## Practical use

This is the controller-level admission recipe:
- compute the exact required prefix floor for the promised margin,
- compare the current state's prefix bits to that floor,
- and reuse the same floor against `7` whenever an all-state guarantee is required.

That removes one more online search problem from the inheritor's path: positive same-deadline live promises can now be admitted directly from integer prefix budgets.
