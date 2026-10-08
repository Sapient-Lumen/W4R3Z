# rev0044 margin-screen hard-frame queue

rev0044 adds a **margin-seeking public hard-frame screen**.  The goal is not to create a new gameplay policy.  The goal is to spend expensive branch rollouts on public decision frames that are more likely to produce decisive counterfactual labels.

The screen uses only public-safe frame features:

```text
action_count
branched_action_count / subset flag when known
public screener vote count / entropy
readable public-profile score spread
previous counterfactual-ranker score spread
base public hard-frame screen score
starting life / starting player
```

The hidden true `GameState` is still used only after public frame selection, inside the offline branch-label referee. Gameplay agents never receive hidden state.

## What changed

New module:

```text
src/muc5/action_margin_screen.py
```

New runner:

```text
scripts/run_rev0044_margin_screen_racer.py
```

The runner trains a tiny ridge-style public-feature model from historical audited counterfactual label rows, exports it to JSON, then uses it to rerank the hard-frame queue before invoking the existing online branch racer.

## Why this is useful

Recent revisions showed that the project is label-quality limited, not model-class limited.  More rows are not enough if most rows are ties.  rev0044 starts treating **decisive-label likelihood** as a first-class target.

The margin screen is intentionally modest.  It is a queueing heuristic, not an oracle.  It can be wrong.  Its purpose is to make future collectors measurable:

```text
public frame features -> predicted margin / queue score -> branch rollouts -> audited actual margin
```
