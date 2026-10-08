# rev0043 online racing results

The hard-frame online racer selected only public-observation frames with action count above the high-action threshold. Every selected situation used a hybrid selector that combines:

- behavior action;
- public-policy screen votes;
- semantic action diversity;
- previous counterfactual-ranker prior when available.

The adaptive branch allocator then used online prefix information only. It did not generate a full fixed matrix and then retroactively choose which rollouts to count.

## Result files

```text
data/rev0043_hard_online_racing_selected.csv
data/rev0043_hard_online_racing_candidates.csv
data/rev0043_hard_online_racing_branch_games.csv
data/rev0043_hard_online_racing_allocations.csv
data/rev0043_hard_online_racing_votes.csv
data/rev0043_hard_online_racing_cpp_transitions.csv
data/rev0043_hard_online_racing_situation_summary.csv
data/rev0043_hard_online_racing_summary.json
```

## Metrics to watch

The key metrics are:

```text
decisive_situations
branch_games
decisive_per_100_rollouts
mean_best_minus_chosen
branch_truncations
cpp_mismatches
cpp_skipped_transitions
```

`decisive_per_100_rollouts` is now first-class because label budget is the bottleneck. More candidate rows are not necessarily better if they are all tied.
