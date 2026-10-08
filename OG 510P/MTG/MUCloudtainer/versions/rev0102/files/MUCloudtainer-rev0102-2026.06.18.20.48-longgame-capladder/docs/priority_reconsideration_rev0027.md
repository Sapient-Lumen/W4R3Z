# rev0027 priority reconsideration

rev0027 completed the previously top-ranked target: outcome-based learned mulligan improvement.

The result was not a dominant mulligan policy.  That changes the priority order.  It suggests the next useful progress is not simply “train another ranker,” but give the learner better targets.

## Current priority order

```text
1. Opening-hand counterfactual probes for mulligan decisions.
2. Larger MAP-Elites races with learned mulligan variants and C++ shadow gates.
3. Meta-rank over denser nontruncated payoff tables.
4. C++ no-choice segment batching under Python fingerprint/observation gates.
5. Search/rollout targets for unchosen legal gameplay alternatives.
```

## Why counterfactual mulligan probes moved up

Outcome-weighted behavior cloning only sees the choice a policy made.  For mulligans, the decision surface is small enough that we can do better:

```text
same opening hand
  keep branch
  take-mulligan branch
  play both branches against sampled opponent/opening contexts
  estimate branch value
```

That would turn the mulligan ranker from “imitate winners” into “learn from paired alternatives.”  It is expensive, but the pregame branch space is tiny compared with full gameplay search.
