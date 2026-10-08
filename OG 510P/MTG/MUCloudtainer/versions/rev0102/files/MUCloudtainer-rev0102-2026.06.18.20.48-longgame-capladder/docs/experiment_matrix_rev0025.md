# rev0025 experiment matrix additions

## New axis: gameplay learner target

```text
imitation_public_policy
imitation_code_policy
pseudo_oracle_mulligan
outcome_weighted_behavior_cloning
future_search_target
future_terminal_advantage
```

rev0025 instantiates `outcome_weighted_behavior_cloning`.

## New strategy-bundle examples

```text
outcome_fjace
outcome_threat_fovr
outcome_counter_wall
mlp_fjace
mlp_threat_fovr
pub_threat_overlord
pub_counter_wall
code_jace60
```

Each remains:

```text
deck + mulligan agent/policy + public gameplay pilot
```

## Required gates for future outcome-trained policies

```text
public DecisionFrame interface
terminal/truncation labels in dataset
promotion gate
statistical gate
sample replay traces
batched C++ trace check
nonzero audit over truncation weighting
```
