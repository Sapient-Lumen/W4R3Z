# rev0041 hard-frame results

rev0041 generated these primary artifacts:

```text
data/rev0041_hard_frame_selected.csv
data/rev0041_hard_frame_candidates.csv
data/rev0041_hard_frame_methods.csv
data/rev0041_hard_frame_branch_games.csv
data/rev0041_hard_frame_votes.csv
data/rev0041_hard_frame_cpp_transitions.csv
data/rev0041_hard_frame_pivot.csv
data/rev0041_hard_frame_summary.json
```

The key file for analysis is:

```text
data/rev0041_hard_frame_pivot.csv
```

It contains one row per selected public situation and compares:

```text
unscreened_budget
screened_vote_budget
hybrid_vote_diverse_ranker
```

All three methods consume the same branch rollout outcomes per situation. The audit therefore measures branch-budget selection, not rollout noise.

## Why no policy was promoted

No policy was promoted in rev0041 because this is an offline label-selection audit. The audit is allowed to use hidden true-state copies inside the referee to create counterfactual labels. A gameplay agent is not allowed to see that state.

## Negative/neutral result

The hard-frame selector successfully increased mean action count and forced subset labels, but it did not produce selector separation in the smoke panel. That is a useful neutral result:

```text
hard-frame queue works
branch budget binds
C++ parity stays clean
selector separation still not visible enough
```

The next build should attach adaptive/racing rollout allocation to this hard-frame queue.
