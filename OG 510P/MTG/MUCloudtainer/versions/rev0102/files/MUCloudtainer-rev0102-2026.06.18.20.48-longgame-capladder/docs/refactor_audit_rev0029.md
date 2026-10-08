# rev0029 refactor and audit notes

## New modules

```text
src/muc5/mulligan_counterfactual.py
src/muc5/nochoice_segments.py
```

`mulligan_counterfactual.py` separates first-look branch-value learning from the older linear mulligan ranker. It deliberately delegates later pregame decisions to `mulligan_outcome_ranker_rev0027`.

`nochoice_segments.py` measures forced DecisionFrame runs without modifying the engine.

## Factory change

`make_mulligan_agent(...)` now recognizes:

```text
mulligan_counterfactual_ranker_rev0029
```

This keeps learned mulligan policies replayable through the same strategy-bundle interface as rule mulligans and prior learned mulligans.

## Audit checks added

The cube audit now verifies:

```text
rev0029 model JSON exists and loads
model feature count matches mulligan-ranker features
factory returns the counterfactual agent by name
18 same-shell strategy bundles exist
432 payoff games were generated
8 replay traces passed
C++ trace checker saw 0 mismatches / 0 skipped events
no-choice segment audit saw 24 games and >1.0 estimated compression ratio
required rev0029 docs/scripts/tests/data files exist
```
