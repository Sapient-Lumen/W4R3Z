# Rematch worlds should budget stateless live deadlines by effective blind horizon

Future inheritors should not budget a same-deadline stateless live controller as though all of its nominal deadline ticks were equally promise-usable.
Under the current geometric-arrival batching model, they are not.

## Exact effective-horizon law

Let `H` be the nominal deadline of a stateless live controller that re-checks after every miss.
Then, for **positive** blind-commit promises, the controller preserves exactly the same promise class as blind commit with horizon

`floor((H + 1) / 2)`.

For general nonnegative margin floors, the exact controller equivalence is slightly broader: the live controller is as promise-safe as choosing the better of immediate close and blind commit with that same effective horizon.

Equivalently:
- a blind-commit promise with minimum timeout `K` is safe under same-deadline stateless live reoptimization iff `H >= 2K - 1`,
- so the promise-safe effective blind horizon of deadline `H` is exactly `floor((H + 1) / 2)`,
- and deadlines `2j - 1` and `2j` are promise-equivalent because both expose effective blind horizon `j`.

This is the controller-level synthesis of the earlier reserve, time-consistency, deficit, and deadline-inflation passes.
Those earlier passes showed:
- the last `K - 1` ticks act as dead reserve,
- multi-tick promises drift at the boundary,
- same-horizon live control pays a geometric haircut,
- and blind-commit value is repaired by adding back `K - 1` deadline ticks.

The new point is that these are all telling the implementor the same planning rule:
**budget only the effective blind horizon, not the nominal live deadline.**

## Operational consequence

For promise preservation, the live controller’s deadline ladder collapses into pairs:
- deadlines `1` and `2` support the same promise-safe class,
- deadlines `3` and `4` support the next class,
- deadlines `5` and `6` support the next class,
- and so on.

So every second nominal deadline tick is dead reserve when the objective is exact preservation of the original blind-commit promise.

## Implementation rule

If the implementation wants same-deadline stateless live control with no silent promise drift, it should:
1. choose the nominal deadline `H`,
2. compute `floor((H + 1) / 2)`,
3. and size admissible promises exactly as though blind commit had only that smaller horizon.

Conversely, if the planner starts from a blind-commit promise that needs timeout `K`, it should provision nominal live deadline `2K - 1`.
Anything smaller silently downgrades the promise class.

## All-state guardrail

The same effective-horizon law holds under the seven-bit all-state lower envelope.
So a universal same-deadline stateless live controller should also budget only `floor((H + 1) / 2)` promise-safe blind ticks, not the full deadline.
