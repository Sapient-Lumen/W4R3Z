# rev0023 — priority reconsideration

The previous priority list was:

```text
1. tiny listwise/MLP or gradient-boosted action ranker
2. C++ batch rollout sketch
3. larger MAP-Elites sequential races
4. mulligan learning
5. meta-rank over denser tables
```

rev0023 completes a first version of item 1 and adds a mulligan policy gate before learned mulligan policies become unavoidable.

## Current priority

```text
1. Learned mulligan agent over explicit pregame legal actions.
2. C++ batch rollout sketch, still under Python replay parity gates.
3. Larger MAP-Elites races using both code policies and learned rankers.
4. Meta-rank only over promoted, nontruncated, sufficiently sampled tables.
5. Tiny policy-improvement loop: use payoff/replay data to train a better ranker, not just imitate baselines.
```

## Why no full C++ rollout yet

The existing C++ transition seam is strong, but the Python shell still owns hidden information, logs, promotion gates, replay, and statistical labeling. A full C++ rollout path should wait until we can preserve those labels without making two divergent simulators.
