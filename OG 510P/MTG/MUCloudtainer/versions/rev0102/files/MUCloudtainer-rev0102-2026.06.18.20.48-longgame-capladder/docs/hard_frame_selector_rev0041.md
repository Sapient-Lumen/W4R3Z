# rev0041 hard-frame selector

rev0041 adds a public-only hard-frame queue before expensive gameplay action-counterfactual branching.

Previous selector audits sampled public decision frames as they appeared. That made it easy for one long game or many low-leverage frames to dominate the label budget. rev0041 instead scores candidate public `DecisionFrame`s before branching them.

The hard-frame screen uses only information that a public policy could see:

```text
action_count
number of unique public-screener votes
vote entropy proxy
readable profile-score spread
previous counterfactual-ranker score spread, if a prior model exists
```

It does not inspect the hidden true state or branch outcomes. The hidden state copy is used only after a frame has been selected by public-only signals, so the offline referee can branch legal alternatives from the identical position.

The screen score is not a value function. It is a queueing heuristic for branch-label budget.

## Smoke result

```text
behavior games:             22
behavior decisions:         3,874
choice frames seen:         1,756
candidate frames seen:        675
selected situations:           12
high-action selected:          12
subset situations:             12
mean action count:          13.33
branch games:                182
branch truncations:            0
C++ checked transitions:  24,016
C++ skipped transitions:       0
C++ mismatches:                0
union-decisive situations:     3
```

This is a useful improvement over rev0040 because the selected frames are genuinely high-action and the branch budget binds. It is still not a promoted policy result.

## Interpretation

The hard-frame queue found harder menus, but the three selector methods still all retained a union-best action in the smoke panel:

```text
hybrid hits union-best:      1.0
unscreened hits union-best:  1.0
screened hits union-best:    1.0
```

So the next issue is not simply “find high-action frames.” It is to combine this hard-frame screen with adaptive branch rollouts so labels become more decisive and the branch budget is spent where it can change the result.
