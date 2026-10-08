# Rematch worlds should not treat multi-tick promises as locally time-consistent

Future inheritors should distinguish between two different notions of “acceptable” under the current geometric-arrival batching model:
- a promise that is reachable by **blindly committing** a finite timeout `K`, and
- a promise that remains valid under **live reoptimization** after every miss.

The previous reserve pass already showed why these differ.
This pass closes the loop.

## Exact time-consistency law

Let `K` be the minimum blind-commit timeout whose expected net value reaches the original margin floor.
Then:
- if `K = 1`, the promise is locally time-consistent under live reoptimization,
- if `K > 1`, the promise is **not** locally time-consistent under live reoptimization.

Why?
At the boundary checkpoint `H = K`, a live countdown controller does not expose the full blind-commit horizon.
It exposes only one usable wait tick, because the last `K - 1` ticks are dead reserve.
So the live boundary value is exactly the one-tick value.
But by minimality of `K > 1`, that one-tick value is still below the original target margin.

So the only finite promises that survive live reoptimization without drift are precisely the promises already met by one more tick.

## Operational consequence

This means a writer cannot have all three of the following at once for a multi-tick promise:
- repeated local checkpoint reoptimization,
- no extra promise state,
- and exact preservation of the original ex-ante margin floor.

For finite multi-tick promises, it must choose one of these alternatives:
1. **blind commit** the whole timeout budget,
2. **accept drift** under live reoptimization,
3. or carry richer state that explicitly tracks promise slack.

## Restoration threshold

The earlier reserve law also gives the repair point:
- a finite schedule with minimum blind-commit timeout `K > 1` first recovers the original promise under live reoptimization at remaining horizon `2K - 1`.

So there are now three salient horizons:
- `1`: the one-tick, locally time-consistent class,
- `K`: the blind-commit threshold,
- `2K - 1`: the first live-reoptimized horizon that restores the original promise.

## All-state guardrail

The same impossibility result holds under the seven-bit lower envelope.
So the inheritor should not assume that a universal multi-tick promise is locally time-consistent either.
If it needs universal no-drift live control, it should restrict itself to one-tick promises or add explicit slack accounting.
