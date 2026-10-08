# rev0037 matched fixed-vs-adaptive label audit

rev0036 added adaptive/racing action-counterfactual labels.  rev0037 asks the next audit question:

```text
If fixed-equal and adaptive-race labelers see the same public situation and the same branch-outcome matrix,
do they produce the same best-action label?
```

This matters because an adaptive labeler can look better merely by seeing different situations or different rollout worlds.  rev0037 avoids that by generating one branch matrix per sampled DecisionFrame, then letting both label methods consume that same matrix.

## Label methods compared

```text
fixed_equal:
  consume 3 rollouts for every selected legal action

adaptive_race:
  consume 1 base rollout for every selected legal action
  spend extra rollouts on current top contenders
  stop early when the top-vs-second margin/confidence looks sufficient
```

The adaptive labeler is evaluated as a label-allocation method, not as a promoted gameplay policy.

## Smoke result

```text
sampled situations:                 12
candidate action/method rows:       54
branch games generated once:        81
fixed total rollouts:               81
adaptive total rollouts:            73
adaptive rollout delta:             -8
adaptive early stops:                4
fixed decisive situations:           2
adaptive decisive situations:        2
best-set agreement rate:             1.0
chosen-best agreement rate:          1.0
branch truncations:                  0
C++ checked branch transitions:  20,358
C++ mismatches:                      0
```

## Interpretation

For this smoke panel, adaptive racing got the same best-action labels while spending fewer branch rollouts.  That is encouraging, but it is not a general theorem.  The decisive-label count is still low.  The correct next use is to keep this matched audit beside future adaptive labelers and reject labelers that save rollout budget by changing labels unpredictably.

## Artifacts

```text
data/rev0037_matched_label_candidates.csv
data/rev0037_matched_label_branch_games.csv
data/rev0037_matched_label_comparison.csv
data/rev0037_matched_label_cpp_transitions.csv
data/rev0037_matched_label_segment_summary.json
```
