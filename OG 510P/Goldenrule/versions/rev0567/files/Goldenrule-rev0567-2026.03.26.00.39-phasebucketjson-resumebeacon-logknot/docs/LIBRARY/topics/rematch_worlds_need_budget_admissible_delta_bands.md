# Rematch worlds need budget-admissible delta bands

## Claim

Once rematch leaderboards publish winner certification, practical-equivalence frontiers, delta-budget frontiers, and hazard bands, the next inheritor-facing object should be a **budget-admissible delta band** rather than a single naked `delta` point.

## Why

A declared smallest effect of interest is supposed to be prespecified and substantively justified, but the operational burden of closing the benchmark is highly uneven across nearby delta values. In the current leave/rematch proxy, deltas that are nearly indistinguishable substantively can sit on opposite sides of a knife-edge leader gap and therefore imply radically different extra paired-seed budgets.

That means two mistakes become easy:

1. **Post hoc threshold shopping**: choosing whichever `delta` looks cheapest after seeing the data.
2. **False precision**: acting as if a single point margin is more meaningful than a contiguous interval of equally defensible margins.

## Current proxy consequence

For the current 9-panel proxy, the admissible set under a `+10` paired-seed closure cap collapses to just two contiguous delta bands, and only one of them lies below `0.01`. Tightening the cap fragments the low-delta region into micro-bands; relaxing it widens the same broad low-delta interval. So the operationally relevant object is not “the best delta” but “which delta interval is admissible under the declared cap, and what anchor inside that interval is being used?”

## Implementor rule

Every rematch benchmark that declares a practical margin should also publish:

- one or more **budget caps** that matter operationally,
- the corresponding **admissible delta bands** under the current closure rule,
- an **anchor delta** for each band,
- and the **counts of material leaders / practical ties / undecided panels** at that anchor.

This keeps the archive compact while making it much harder to launder a knife-edge, post hoc threshold choice into an apparently principled SESOI.
