# Rematch worlds should treat live countdowns as usable wait windows plus dead reserve

Future inheritors should be careful not to confuse two different objects:
- the value of **blindly committing** all remaining deadline ticks right now, and
- the value of a **live countdown policy** that re-checks after every miss and may close early.

The previous deadline-countdown pass characterized the first object.
This pass turns that into the second one.

## Setup

Fix a realized feasible state with prefix cost `state_prefix_bits`, current shared-state batch length `n`, same-state arrival hazard `p`, hold cost `c`, realized margin floor `m`, and remaining deadline `H`.

Let `K` be the minimum timeout from the earlier target-batch timeout law: the smallest blind-commit timeout whose expected net value meets `m`.

## Exact reserve law

Under a **live** countdown policy that re-checks after every miss and continues exactly while the remaining horizon still satisfies the previous countdown threshold, the actual continuation value is

`F(max(H - K + 1, 0))`

where `F(T)` is the earlier fixed-timeout wait-value law.

So the last `K - 1` deadline ticks behave as a **dead reserve**.
They are needed to justify continuing locally, but they are not part of the economically usable wait window under repeated reoptimization.

Equivalently:
- blind commit of all remaining ticks uses horizon `H`,
- live countdown reoptimization uses only horizon `max(H - K + 1, 0)`.

## Margin-preservation consequence

This distinction matters.
A batch can satisfy the blind-commit threshold `H >= K` and still fail to preserve the original promised margin under live checkpoint reoptimization.

Because the live value uses only `H - K + 1` effective ticks, the original promise is preserved exactly when

`H >= 2K - 1`

for finite schedules.

So there are two separate horizons now:
- `K`: enough horizon to justify **continuing locally**,
- `2K - 1`: enough horizon to preserve the **original ex-ante margin promise** even after live re-checking.

## Implementation lesson

A robust writer should decide which semantics it wants:

1. **Blind-commit semantics**
   - Once it continues, it conceptually spends the whole remaining timeout budget.
   - Then `K` is the right threshold.

2. **Live-reoptimized semantics**
   - It re-checks after misses and may close early.
   - Then it should understand that only `H - K + 1` ticks are economically usable.
   - If it still wants to preserve the original margin promise from the current checkpoint, it should require `H >= 2K - 1`.

This is the tighter implementor rule the archive was missing.

## Universal guardrail

The same reserve law applies to the all-state seven-bit envelope.
Just substitute `state_prefix_bits = 7`.
That yields a conservative live-countdown reserve and a conservative `2K - 1` promise-preservation guardrail that is safe across all realized states on the audited path.
