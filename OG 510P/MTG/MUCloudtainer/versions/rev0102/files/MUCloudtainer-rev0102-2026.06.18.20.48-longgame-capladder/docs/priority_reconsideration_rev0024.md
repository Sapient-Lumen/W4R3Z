# rev0024 priority reconsideration

The previous priority was:

```text
learned mulligan agent
C++ batch rollout sketch
larger MAP-Elites races
outcome-weighted action-ranker improvement
meta-rank over denser promoted tables
```

rev0024 completes the first item at seed scale. The new priority order is:

```text
1. Outcome-weighted policy improvement for gameplay actions.
2. C++ batch rollout sketch under Python fingerprint gates.
3. Learned mulligan improvement from actual game outcomes instead of pseudo-oracle labels.
4. Larger MAP-Elites races with learned mulligan variants included.
5. Meta-rank over denser nontruncated promoted tables.
```

Why not immediately full C++?

Because fast wrong rollouts would poison every learning method. The safer plan is to continue moving stable slices into C++ only after Python replay and C++ trace parity checks remain boring.

Why not another imitation ranker?

The MLP and linear rankers already show that imitation works mechanically. The next improvement should use outcomes, not just mimic current weak policies.
