# rev0034 priority reconsideration

The project has three live fronts:

1. **Better labels for unchosen gameplay actions.**
2. **C++ batching where the simulator is actually hot.**
3. **Population evaluation over deck + mulligan + pilot bundles.**

rev0034 chooses the first front.  The reason is that the first gameplay counterfactual ranker in rev0033 was label-starved.  A stronger C++ core would not help if the target labels are too noisy to teach useful policy improvements.

## Current priority order

```text
1. Scale action-counterfactual labels further and track label uncertainty.
2. Add budgeted/search-style branch selection so high-action frames are not ignored forever.
3. No-choice segment execution benchmark under Python pre/post SIGv2 gates.
4. Larger MAP-Elites races including rev0034 counterfactual gameplay rankers.
5. Meta-rank over denser, nontruncated promoted payoff tables.
```

## Pushback

The rev0034 model should not be treated as a strong player merely because it is trained from counterfactuals.  It is still a small linear model trained from a small branch budget.  The more important artifact is the branch-label pipeline plus noise audit.
