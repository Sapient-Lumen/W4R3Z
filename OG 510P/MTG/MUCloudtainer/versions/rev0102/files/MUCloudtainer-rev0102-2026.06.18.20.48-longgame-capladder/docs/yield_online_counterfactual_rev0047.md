# rev0047 Yield-Screened Online Action Counterfactuals

rev0047 turns the rev0046 label-yield screen from a matched queue audit into a production-shaped label collector.

The flow is:

```text
public behavior games
  -> public hard-frame candidate pool
  -> yield-screen queue
  -> hybrid action subset selection
  -> online adaptive branch racing
  -> C++ transition shadow check
  -> action-counterfactual candidate rows
```

The yield screen is still only a queueing model. It receives public `DecisionFrame`-derived features such as action count, vote entropy, profile-score spread, ranker-score spread, and starting-life flags. It never sees the true hidden state, opponent hand, or library order.

Hidden state is used only by the offline branch-label referee after a frame has already been selected. That is the same boundary as prior action-counterfactual collectors: agents do not get hidden state, but the label generator may copy the true referee state to compare legal alternatives from the same point.

## Archived smoke collection

`data/rev0047_yield_online_counterfactual_summary.json` reports:

```text
pool rows:                 64
yield-selected frames:     16
candidate action rows:     94
branch games:              182
branch truncations:        0
C++ checked transitions:   24,673
C++ skipped transitions:   0
C++ mismatches:            0
decisive situations:       3
decisive / 100 rollouts:   1.648
```

This is not a large label budget. It is a clean continuation of the label-yield path.

## Interpretation

The yield queue produced usable labels, but label density remains the bottleneck. Most selected situations still tied under the small branch-rollout budget. The next collector should keep the yield queue but improve the branch allocator or frame screen toward genuinely high-margin choices.

