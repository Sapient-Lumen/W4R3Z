# rev0036 adaptive action-counterfactual labels

rev0036 changes the gameplay counterfactual labeler from a fixed rollout budget to a small racing loop.

The old shape was:

```text
sample public DecisionFrame
branch selected legal actions
run exactly N rollouts per action
train from mean branch outcome
```

The new shape is:

```text
sample public DecisionFrame
select legal actions, using the rev0035 budget selector when needed
run one base rollout for every selected action
compute current best action and runner-up
spend extra rollouts on the top contenders while the margin is uncertain
stop early when the gap/confidence looks sufficient
```

This is still an offline label generator.  Agents do not see the hidden true state.  The collector copies the true referee state only to create fair branches from the same position.

## Why this matters

The limiting resource is no longer merely row count.  Many labels are ties or noisy.  Adaptive racing tries to spend rollouts where they can change the label, instead of giving obviously bad or redundant actions the same budget as the likely best actions.

The rev0036 smoke run produced:

```text
sampled situations:          10
candidate actions:           22
branch games:                49
base rollouts/action:         1
adaptive extra rollouts:     27
early stops:                  3
branch terminal games:       49
branch truncations:           0
C++ branch transitions:  13,135
C++ branch mismatches:        0
decisive situations:          6
behavior-chosen-best rate:  0.7
```

This is a small run, but it proves the adaptive allocation seam works and records enough metadata to avoid overclaiming.

## Label metadata

Candidate rows now include:

```text
branch_rollouts
base_rollouts_per_action
adaptive_extra_rollouts_for_action
total_adaptive_extra_rollouts
adaptive_stopped_early
situation_best_margin
label_confidence_proxy
branched_subset
budget_reason
```

`label_confidence_proxy` remains a cheap diagnostic, not a statistical theorem.

## Pushback

The training set is deliberately small in this revision so the archive stays fast to regenerate inside the cloudtainer.  The model should not be read as a strong strategic result.  The actual win is that the labeler can now spend branch budget adaptively and still pass C++ parity checks.
