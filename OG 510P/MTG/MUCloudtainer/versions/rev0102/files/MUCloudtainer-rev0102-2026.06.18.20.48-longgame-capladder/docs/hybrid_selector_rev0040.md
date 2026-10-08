# rev0040 — Hybrid branch selector

rev0038 showed that public-policy disagreement is a useful way to find contested gameplay frames. rev0039 showed that **vote priority alone** can be worse than an unscreened diversity budget. rev0040 adds a third selector:

```text
hybrid_vote_diverse_ranker
```

It is not a policy and is not used during normal games. It is an offline branch-budget allocator for action-counterfactual labels.

## Selector ingredients

For a public `DecisionFrame`, the selector keeps:

```text
1. behavior_chosen action
2. at most two public-screen voted actions
3. a cheap top-prior action
4. semantic diversity representatives
5. combined-score fill if budget remains
```

The cheap prior currently uses:

```text
readable public-profile scores
+ rev0034 counterfactual-ranker score when available
```

The ranker prior is intentionally weakly weighted. It should nudge branch selection, not dominate it.

## Why this matters

Action-counterfactual labels are expensive because each branched action needs rollout games. The question is not “which action is best?” directly; the question is:

```text
Which legal actions should receive expensive branch rollouts?
```

rev0040 compares three answers on matched situations:

```text
unscreened_budget:
  behavior + diversity

screened_vote_budget:
  behavior + public-screen votes + diversity fill

hybrid_vote_diverse_ranker:
  behavior + limited votes + diversity + cheap prior
```

All three consume the same branch rollout outcomes, so method differences come from branch selection rather than rollout noise.
