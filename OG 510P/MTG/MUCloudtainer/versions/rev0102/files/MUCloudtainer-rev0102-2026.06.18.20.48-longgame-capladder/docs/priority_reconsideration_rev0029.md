# rev0029 priority reconsideration

The best next priority changed slightly.

rev0028 showed we can create paired keep-vs-mulligan branch data. rev0029 turns that into a policy, but the model is noisy because each branch currently gets one rollout.

So the next best work is not a more complex neural model. It is better counterfactual targets.

Current order:

```text
1. Repeat-rollout opening counterfactuals to reduce branch label noise.
2. No-choice segment fingerprint instrumentation for C++ batching.
3. Larger MAP-Elites races including counterfactual mulligan variants.
4. Search/rollout targets for unchosen gameplay actions.
5. Meta-rank over denser nontruncated payoff tables.
```

Key lesson: counterfactual learning is the right shape, but one rollout per branch is too noisy for strong claims.
