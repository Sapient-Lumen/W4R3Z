# rev0024 learned mulligan ranker

rev0024 makes mulligan agency a learned/evaluable object instead of only a named deterministic policy.

The new policy is:

```text
mulligan_ranker_rev0024
```

It consumes the same explicit pregame action surface introduced earlier:

```text
MULLIGAN_KEEP
MULLIGAN_TAKE
MULLIGAN_BOTTOM(card)
```

The ranker is JSON-backed, not pickle-backed:

```text
data/rev0024_mulligan_ranker_model.json
```

It contains two linear models:

```text
keep model:       observation -> keep/take logit
bottom model:     observation + candidate card -> bottom-card score
```

The feature vector includes:

```text
stage flags
mulligans taken
hand size
library count
bottom count remaining
starting life 20/40 flags
deck size 40/60 flags
hand counts / hand fractions
deck fractions
candidate-card one-hot flags
small public opening-hand hints
```

The pregame observation was refactored to include the construction context the agent is allowed to know:

```text
starting_life
deck_counts
```

This is construction/pregame information, not hidden opponent hand/library information.

## Training source

The first model is **pseudo-oracle seeded**, not discovered by RL.

Training labels come from a transparent opening-hand quality function in `src/muc5/mulligan_ranker.py`. That function values functional mana, interaction, Force reliability, Jace/Overlord threat access, life-total context, and deck composition. This is deliberately weaker than a learned gameplay EV oracle, but it gives us a safe frozen policy object to test the pipeline.

Generated training artifacts:

```text
data/rev0024_mulligan_ranker_keep_training.csv
data/rev0024_mulligan_ranker_bottom_training.csv
data/rev0024_mulligan_ranker_model.json
```

Smoke training metrics from this revision:

```text
keep test accuracy:              ~0.9913
keep ROC AUC:                    ~0.9973
bottom-card top-1 accuracy:      ~0.7873
bottom random-slot baseline:     ~0.3353
bottom MRR:                      ~0.8819
```

These metrics only say the model learned the pseudo-oracle labels. They do not mean it learned perfect MUC mulligans.

## Gameplay evaluation

The learned policy enters the same bundle format as every other strategy:

```text
deck + mulligan agent + public gameplay pilot
```

rev0024 evaluates three fixed deck/pilot shells under four mulligan policies:

```text
keep_always
land_band
land_band_business
mulligan_ranker_rev0024
```

Generated payoff artifacts:

```text
data/rev0024_learned_mulligan_games.csv
data/rev0024_learned_mulligan_aggregate.csv
data/rev0024_learned_mulligan_standings.csv
data/rev0024_learned_mulligan_same_shell.csv
data/rev0024_learned_mulligan_pairwise.csv
data/rev0024_learned_mulligan_stat_standings.csv
data/rev0024_learned_mulligan_summary.json
```

Smoke table:

```text
12 strategy bundles
576 games
0 truncations
promotion gate passed
statistical gate passed
8 / 8 replay traces passed
1,953 C++ trace events checked
0 skipped C++ events
0 C++ mismatches
```

In this smoke run, the learned policy helped the `wall_counter` shell and the `overlord_threat` shell but was worse than `land_band_business` for the `fjace_code` shell. That is useful: learned pregame policy is now testable per shell instead of being treated as globally good or bad.
