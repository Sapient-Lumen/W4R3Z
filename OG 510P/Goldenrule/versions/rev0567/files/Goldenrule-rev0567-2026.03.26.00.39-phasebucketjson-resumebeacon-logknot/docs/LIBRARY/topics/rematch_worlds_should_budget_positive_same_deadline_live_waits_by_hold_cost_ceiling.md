# Rematch worlds should budget positive same-deadline live waits by hold-cost ceiling

Future inheritors should not decide whether a same-deadline stateless live wait is still affordable by re-solving timeout tables online.
Under the current geometric-arrival model, there is a direct closed-form per-tick hold-cost ceiling.

## Exact positive live hold-cost ceiling law

Let:
- `H` be the nominal deadline of a stateless live controller that re-checks after every miss,
- `n` be the current batch length,
- `p` be the per-tick arrival hazard,
- `m > 0` be the promised realized margin floor,
- and `state_prefix_bits` be the current shared-state gain numerator.

Then same-deadline stateless live control preserves the original **positive** promise exactly iff

`hold_cost <= p * (state_prefix_bits / (n(n + 1)) - m / (1 - (1 - p)^floor((H + 1) / 2)))`.

So the maximum admissible per-tick hold cost is exactly

`p * (state_prefix_bits / (n(n + 1)) - m / (1 - (1 - p)^floor((H + 1) / 2)))`.

This is just the blind-commit hold-cost ceiling evaluated at the effective blind horizon

`floor((H + 1) / 2)`.

## Practical interpretation

This gives the inheritor a one-line affordability test:
1. reduce nominal live deadline `H` to effective blind horizon `floor((H + 1) / 2)`,
2. compute the closed-form hold-cost ceiling above,
3. and continue waiting only while estimated per-tick hold cost stays at or below that ceiling.

Equivalent consequences:
- if the ceiling is negative, the positive promise is impossible even at zero hold cost,
- if the ceiling is zero, only a zero-cost wait can preserve the promise,
- and if the ceiling is positive, the promise survives exactly up to that threshold and fails immediately above it.

## Odd/even deadline ladder

Because the ceiling depends only on `floor((H + 1) / 2)`, deadlines `2j - 1` and `2j` have the same positive live hold-cost ceiling.
The ceiling only improves when the nominal deadline climbs to the next odd rung.
So positive same-deadline live affordability advances on the same odd ladder as the earlier minimum-deadline law.

## Zero-margin edge case

At margin floor `m = 0`, immediate close already realizes value `0`.
So there is no finite same-deadline live hold-cost ceiling for promise safety alone: the controller can always close immediately instead of paying the wait.

## All-state guardrail

The same law holds under the seven-bit all-state lower envelope after replacing `state_prefix_bits` by `7`.
So a universal same-deadline stateless live controller can also make affordability decisions from one closed-form hold-cost ceiling.
