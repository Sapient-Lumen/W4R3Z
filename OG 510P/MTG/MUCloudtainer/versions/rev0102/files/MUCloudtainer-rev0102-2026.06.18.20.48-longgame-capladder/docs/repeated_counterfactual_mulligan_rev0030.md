# rev0030 repeated counterfactual mulligan ranker

rev0028 created the first keep-vs-mulligan counterfactual seam. rev0029 trained a first-look mulligan model from one rollout per branch. rev0030 repeats that branch rollout so the label is no longer a single terminal game.

The experimental unit is still narrow and hidden-information safe:

```text
same first seven-card look
  branch A: force KEEP
  branch B: force TAKE MULLIGAN
same opponent pregame hand/library
same construction context
same gameplay pilots
multiple gameplay rollout seeds
average branch outcomes
```

This produces a first-look target:

```text
mulligan_minus_keep_mean = mean(score after first mulligan branch) - mean(score after keep branch)
```

The new model is:

```text
mulligan_repeated_counterfactual_ranker_rev0030
```

It is intentionally limited:

```text
first keep/take decision: learned from repeated branch means
later keep/take decisions: delegate to mulligan_outcome_ranker_rev0027
bottom-card decisions: delegate to mulligan_outcome_ranker_rev0027
```

That contract matters. A first-look counterfactual dataset should not pretend to teach every London-mulligan branch.

## Generated data

```text
data/rev0030_repeated_opening_counterfactual_branch_games.csv
data/rev0030_repeated_opening_counterfactual_pairs.csv
data/rev0030_repeated_opening_counterfactual_cpp_transitions.csv
data/rev0030_repeated_opening_counterfactual_summary.json

data/rev0030_repeated_counterfactual_training_rows.csv
data/rev0030_repeated_counterfactual_mulligan_model.json

data/rev0030_repeated_counterfactual_mulligan_games.csv
data/rev0030_repeated_counterfactual_mulligan_same_shell.csv
data/rev0030_repeated_counterfactual_mulligan_summary.json
```

Smoke numbers from the archived run:

```text
paired opening situations:     24
rollouts per branch:           2
branch games:                  96
C++-checked transitions:       25,523
C++ skipped transitions:       0
C++ mismatches:                0
truncations:                   0

mulligan-better pairs:         3
keep-better pairs:             4
tie pairs:                     17
mean mulligan-minus-keep:     -0.0625
```

The resulting same-shell payoff panel used 21 strategy bundles:

```text
3 deck/pilot shells
× 7 mulligan policies
= 21 bundles
```

Policies:

```text
keep_always
land_band
land_band_business
mulligan_ranker_rev0024
mulligan_outcome_ranker_rev0027
mulligan_counterfactual_ranker_rev0029
mulligan_repeated_counterfactual_ranker_rev0030
```

The payoff table passed promotion, statistical, replay, and C++ trace gates.

## Pushback

This is the right shape, but still not enough data for strong mulligan theory. The rev0030 training set had only 24 paired opening situations and only 6 non-tie examples. The reported non-tie sign accuracy is therefore not meaningful as a success claim. The value of rev0030 is the infrastructure: repeated branch rollouts, averaged labels, and an agent that can enter normal strategy bundles.

The next stronger version should increase:

```text
paired opening situations
rollouts per branch
policy/deck shells
opponent diversity
```

before treating the learned first-look policy as strategic evidence.
