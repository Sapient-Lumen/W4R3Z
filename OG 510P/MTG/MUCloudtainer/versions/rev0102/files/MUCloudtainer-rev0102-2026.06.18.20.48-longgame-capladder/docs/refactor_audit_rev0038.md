# rev0038 refactor/audit notes

New module:

```text
src/muc5/action_disagreement.py
```

New script:

```text
scripts/run_rev0038_disagreement_screened_counterfactual.py
```

New tests:

```text
tests/test_rev0038_disagreement_screened.py
```

Refactor focus:

```text
sample public frames by policy disagreement
record screen votes as first-class audit rows
train a standard JSON counterfactual ranker at data/rev0038_counterfactual_action_ranker_model.json
use the existing generic rev counterfactual-ranker agent loader
add a rev0038 strategy panel in strategy_sets.py
```

Fairness boundary:

```text
screening policies receive only DecisionFrame
branch labeler may copy hidden GameState offline
trained policy receives only DecisionFrame at play time
C++ remains shadow-checked against Python signatures
```

Audit additions check:

```text
rev0038 output rows match summary counts
screened labels have zero C++ skips/mismatches
mean unique screen votes is at least two
ranker model loads and has the expected feature count
rev0038 generic ranker aliases load
promotion/statistical/replay/C++ gates pass for the payoff smoke table
```
