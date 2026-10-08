# Rematch worlds should run positive batches by precomputed remaining-horizon countdowns

Future inheritors should treat the live writer loop as a **countdown controller**, not as a repeated miss-age intuition pump.

The earlier geometric-arrival passes already gave the two ingredients:
- the exact minimum timeout needed for a fixed batch length and realized margin promise,
- and the checkpoint-extension fact that elapsed no-arrival streaks do not change future value under the current model.

Putting them together yields a simpler operational rule.

## Exact rule

Fix a realized feasible state with prefix cost `state_prefix_bits`, current shared-state batch length `n`, same-state arrival hazard `p`, hold cost `c`, and realized margin floor `m`.

At any checkpoint with `H` ticks remaining until the batch must close, continue exactly when

`(1 - (1 - p)^H) * (state_prefix_bits / (n(n+1)) - c / p) >= m`

for `p > 0`.

Equivalently:
- compute the minimum timeout `K` from the earlier target-batch-timeout law,
- then continue exactly while `H >= K`,
- and close immediately once the remaining horizon drops below `K`.

## Operational consequence

So a writer does **not** need to re-solve batch economics after every empty tick.
It only needs to track a few quantities:
- the current shared state,
- the current batch length,
- the arrival/hold-cost assumptions,
- the promised realized margin floor,
- and the remaining ticks until the local deadline.

If those first four inputs have not changed, then the whole live control problem collapses to decrementing one countdown.

## Three schedule classes

The earlier timeout inversion still partitions policies cleanly:
- **finite**: some finite `K` exists, so continue while `H >= K`;
- **asymptotic-only**: the promise sits exactly on the asymptotic boundary, so no finite remaining horizon suffices unless certainty already collapses the case into the finite class;
- **impossible**: the requested promise exceeds checkpoint-feasible value and should be rejected or downsized.

## All-state guardrail

On the current path, the all-state lower envelope remains the seven-bit family.
So the universal countdown rule is the same inequality with `state_prefix_bits = 7`:

`(1 - (1 - p)^H) * (7 / (n(n+1)) - c / p) >= m`

That gives a conservative countdown threshold that is safe for every realized state on the audited path.

## How to use it

A good implementation path is now:
1. decide whether the batch promise is worth pursuing at all,
2. precompute the minimum viable horizon for that promise,
3. keep the batch open while the remaining deadline is at least that large,
4. and only recompute if state, hazard, cost, or promise changes.

Under the current geometric-arrival model, elapsed miss age by itself never belongs in that loop.
