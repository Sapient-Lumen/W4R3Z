# rev0025 outcome-weighted gameplay ranker

rev0025 is the first gameplay policy-improvement step that is not pure imitation.  Earlier rankers learned to copy the action chosen by readable public/code policies.  The new dataset records the same public `DecisionFrame` rows, but waits until the game ends and tags each acting-player decision with the terminal result.

The training rule is intentionally small and auditable:

```text
terminal win trajectory   -> sample weight 1.00
terminal loss trajectory  -> sample weight 0.15
nonterminal truncation    -> sample weight 0.00
```

This is still behavior cloning: the model learns from actions that were actually chosen by behavior policies.  The improvement attempt is that successful trajectories speak much louder than losing trajectories, and truncation games do not become positive training examples.

## New files

```text
src/muc5/outcome_training.py
scripts/run_rev0025_outcome_ranker.py
data/rev0025_outcome_ranker_training_dataset.csv
data/rev0025_outcome_ranker_model.json
data/rev0025_outcome_ranker_feature_importance.csv
```

## Public safety contract

Rows are built from:

```text
DecisionFrame.observation
DecisionFrame.legal_actions
context_feature_dict(...)
action_feature_dict(...)
```

They do not include opponent hand, hidden libraries, omniscient `GameState`, or future cards.  Terminal outcome labels are added only after the game is finished.

## Smoke training metrics

```text
raw candidate-action rows:       64,897
raw decision frames:             29,831
usable weighted rows:            64,897
training feature count:          81
test top-1 action accuracy:      ~0.9106
random-slot baseline:            ~0.7230
test mean reciprocal rank:       ~0.9430
```

These metrics say that the model learned the weighted behavior-policy labels.  They do not prove optimal play.

## Smoke payoff result

The evaluation panel used 8 strategy bundles and 256 public DecisionFrame games.  It passed:

```text
promotion gate
statistical gate
8/8 deterministic replay samples
1,943 C++ trace events, zero skipped, zero mismatches
```

Top smoke standing:

```text
outcome_counter_wall: mean score 0.703125 over 64 seat-symmetric games
```

That is a useful signal, but not a claim-ready strategic theorem.  It should feed larger races and denser payoff tables.
