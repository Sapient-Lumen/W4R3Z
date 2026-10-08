# Rematch worlds should budget positive same-deadline live promises on odd deadlines

Future inheritors should not treat every nominal same-deadline stateless live horizon as a distinct positive promise class.
Under the current geometric-arrival model, they are not distinct.

## Exact minimum live-deadline law

Let `K` be the minimum blind-commit timeout needed to preserve a **positive** realized margin promise for a given batch, state, arrival hazard, and hold cost.
Then the minimum nominal deadline of a stateless live controller that preserves that same promise is exactly

`2K - 1`.

Equivalently:
- positive same-deadline live promises enter on the odd ladder `1, 3, 5, ...`,
- every even deadline `2j` duplicates the positive promise class of `2j - 1`,
- and no positive promise is ever uniquely admitted for the first time by an even nominal deadline.

This is the direct planning form of the earlier effective-horizon law.
Those earlier passes showed that same-deadline live control preserves exactly the blind-commit promise class with effective horizon `floor((H + 1) / 2)`.
Solving that equivalence for the first feasible `H` yields the odd-ladder minimum directly.

## Zero-floor shortcut

At margin floor `m = 0`, the controller can always close immediately.
So the minimum same-deadline live deadline is simply

`1`

for every batch and state context.
There is no need to climb the odd ladder unless the promise is strictly positive.

## Operational consequence

If the planner starts from a positive batch promise, it should:
1. solve the minimum blind-commit timeout `K`,
2. provision same-deadline live control at nominal deadline `2K - 1`,
3. and regard deadline `2K` as economically redundant for promise preservation.

That means the positive controller frontier advances one odd rung at a time.
The even ticks are reserve duplicates, not new promise classes.

## All-state guardrail

The same odd-ladder minimum-deadline law holds under the seven-bit all-state lower envelope.
So a universal same-deadline stateless live controller should also provision positive promises at `2K - 1`, with `K` computed from the universal blind-commit law.
