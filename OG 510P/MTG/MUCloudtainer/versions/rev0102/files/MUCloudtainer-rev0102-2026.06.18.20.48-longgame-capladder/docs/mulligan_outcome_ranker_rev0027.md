# rev0027 mulligan outcome ranker

rev0024 trained a learned mulligan policy from a transparent opening-hand pseudo-oracle.  That was useful because it made mulligans agent-facing, but it did not learn from actual game results.

rev0027 adds a second learned pregame policy:

```text
mulligan_outcome_ranker_rev0027
```

It keeps the same explicit London-mulligan action grammar:

```text
MULLIGAN_KEEP
MULLIGAN_TAKE
MULLIGAN_BOTTOM(card)
```

and the same public/pregame information boundary:

```text
own current hand
own registered deck counts
starting life total
mulligans already taken
bottom cards still required
```

It still does **not** see the opponent's opening hand, opponent library, or future draws.

## Training source

The new training table is built from actual terminal games.  The collector runs public DecisionFrame games using a behavior panel of rule mulligans plus the rev0024 pseudo-oracle ranker.  It records each player's mulligan decisions, waits until the game ends, and gives each pregame decision a terminal score from the acting player's perspective.

The weighting rule is conservative:

```text
terminal win:       weight 1.00
terminal loss:      weight 0.08
nonterminal draw:   weight 0.00
```

So a truncation/draw-half outcome is never a positive teacher.

## Model shape

The model reuses the rev0024 JSON schema:

```text
keep/take logistic model:
  MulliganObservation -> keep logit

bottom-card logistic model:
  MulliganObservation + candidate card -> bottom score
```

The model file is:

```text
data/rev0027_mulligan_outcome_ranker_model.json
```

and the registered agent name is:

```text
mulligan_outcome_ranker_rev0027
```

## Smoke result

Training collection:

```text
288 behavior-policy games
648 mulligan decision events
612 keep/take rows
124 bottom candidate rows
0 truncated training games
```

Training metrics:

```text
keep accuracy:            about 0.967
keep ROC AUC:             about 0.985
bottom top-1 accuracy:    about 0.667
bottom random baseline:   about 0.319
```

Evaluation panel:

```text
15 strategy bundles
900 public payoff games
450 aggregate rows
8 / 8 replay traces passed
2,112 C++ trace events checked
0 skipped C++ events
0 C++ mismatches
promotion gate passed
statistical gate passed
```

## Interpretation

The outcome mulligan ranker is a real strategy-bundle component, but it did **not** dominate the rule or pseudo-oracle mulligan policies in the smoke table.  That is useful, not disappointing: outcome-weighted behavior cloning can only learn from chosen behavior-policy actions.  It still does not know counterfactual values for unchosen mulligan decisions.

The next stronger version should use either larger behavior diversity, explicit mulligan search targets, or replayable counterfactual probes over opening hands.
