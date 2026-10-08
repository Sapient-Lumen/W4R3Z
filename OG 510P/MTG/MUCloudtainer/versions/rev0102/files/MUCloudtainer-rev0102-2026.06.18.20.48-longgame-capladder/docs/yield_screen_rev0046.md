# rev0046 yield-screen queue

rev0046 adds a public-feature queue model for action-counterfactual label collection.  The previous margin screen tried to predict raw branch margin.  The new screen targets a more operational quantity:

```text
decisive labels per rollout
```

The point is not to find frames that look strategically dramatic.  The point is to spend expensive branch rollouts where a counterfactual label is likely to be both decisive and cheap.

## Boundary

The yield screen is not a gameplay policy.  It receives only public-safe frame features:

```text
action_count
screen_unique_votes
screen_vote_entropy_proxy
profile_spread
ranker_spread
screen_score
starting_life_40
starting_player
```

It does not inspect the hidden true state, opponent hand, future library order, or branch outcomes.  Hidden state is used only by the offline branch-label referee after a public frame has been selected.

## Training target

Historical audited counterfactual candidate files are aggregated by `situation_id`.  Each situation receives:

```text
decisive = 1 if situation_best_margin > 0 else 0
total_branch_rollouts = sum(branch_rollouts across candidate actions)
label_yield_per_100_rollouts = 100 * decisive / total_branch_rollouts
```

The rev0046 model is a tiny ridge-style linear model over public features.  It is intentionally small and JSON-backed so future sandpeople can read or replace it without introducing opaque binary state.

## Why this exists

Recent revisions were label-quality limited.  Many branch rollouts ended in ties, and the learned gameplay rankers were limited by noisy or nondecisive labels.  The yield screen is one attempt to improve the label economy before spending more CPU on larger branch collections.
