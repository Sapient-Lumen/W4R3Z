# rev0028 priority reconsideration

rev0028 completed the previous top priority: opening-hand keep-vs-mulligan counterfactual probes.

## What changed

The mulligan problem now has three learning targets:

```text
rev0024: pseudo-oracle opening-hand quality labels
rev0027: terminal outcome-weighted behavior choices
rev0028: paired keep-vs-mulligan branch outcomes from the same first seven-card look
```

The paired branch target is the strongest of the three, but it is also noisier and more expensive because it requires gameplay rollouts.

## Current priority order

```text
1. Train a counterfactual mulligan value/ranker from rev0028 branch pairs.
2. Add no-choice segment instrumentation for eventual C++ batching.
3. Larger MAP-Elites races with learned/counterfactual mulligan variants and C++ shadow gates.
4. Meta-rank over denser nontruncated payoff tables.
5. Search/rollout targets for unchosen gameplay actions.
```

## Pushback

Do not overfit to the rev0028 paired table.  It has only 72 opening situations and one branch game per branch.  It should seed the counterfactual-learning path, not decide final mulligan theory.

The next learned mulligan agent should either train on a much larger branch table or use the rev0028 shape as a smoke test only.
