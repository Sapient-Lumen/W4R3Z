# Rematch worlds should gate positive same-deadline live promises by arrival floor

Future inheritors should not treat arrival-hazard estimation as a high-dimensional search problem once batch length, hold cost, promised margin, and nominal live deadline are fixed.
Under the current geometric-arrival model, positive same-deadline stateless live promise admission is monotone in the arrival hazard.
So each fixed context has at most one positive arrival floor.

## Exact monotonicity law

Let

- `H` be the nominal deadline of a same-deadline stateless live controller,
- `k = floor((H + 1) / 2)` be the effective blind horizon,
- `n` be the batch length,
- `p` be the per-tick arrival hazard,
- `hold_cost` be the per-tick waiting cost,
- and `prefix_budget = state_prefix_bits / (n(n + 1))`.

Then the raw positive branch of the maximum preservable realized margin is

`R_k(p) = (1 - (1 - p)^k) * (prefix_budget - hold_cost / p)`.

Its derivative satisfies

`p^2 * R_k'(p) = k * p^2 * (1 - p)^(k - 1) * prefix_budget + hold_cost * p * sum_{i=0}^{k-2}((1 - p)^i - (1 - p)^(k - 1))`.

Every term on the right is nonnegative for `0 < p <= 1`.
So `R_k(p)` is nondecreasing in `p`, and positive-promise admission is upward-closed in the arrival hazard.
Once a positive same-deadline live promise is safe at some hazard, it stays safe for every larger hazard.

## Arrival-floor interpretation

Fix `n`, `hold_cost`, `H`, and a positive realized margin promise `m`.
Then there are only two cases:

- if `prefix_budget - hold_cost < m`, even certain arrival does not cover the promise, so no positive arrival floor exists,
- if `prefix_budget - hold_cost >= m`, the positive promise has a unique minimum arrival floor `p* in (0, 1]` and the promise is safe exactly for `p >= p*`.

So an inheritor can compile hazard uncertainty down to a one-dimensional threshold test.
The controller does not need to reason about multiple disconnected “safe hazard bands.”

## One-tick closed form

When `k = 1`, the threshold is exact in one line:

`p * prefix_budget - hold_cost >= m`

so the positive arrival floor is

`p* = (hold_cost + m) / prefix_budget`

whenever that quantity is at most `1`; otherwise the promise is impossible.

## Universal seven-bit guardrail

The same law holds under the all-state seven-bit lower envelope after replacing `prefix_budget` by `7 / (n(n + 1))`.
So the universal controller can also gate positive same-deadline live promises by a single upward-closed arrival floor.
