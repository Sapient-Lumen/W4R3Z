# rev0036 refactor and audit notes

## New files

```text
src/muc5/action_racing.py
scripts/run_rev0036_adaptive_action_counterfactual.py
tests/test_rev0036_adaptive_actioncf.py
```

## Refactor

`public_agents.py` now has a generic counterfactual-ranker alias parser.  Future models that follow the standard file convention:

```text
data/<rev>_counterfactual_action_ranker_model.json
```

can be loaded through names like:

```text
counterfactual_linear_ranker_rev0036
counterfactual_ranker_blend_threat_rev0036
counterfactual_ranker_blend_counter_rev0036
counterfactual_ranker_blend_patient_rev0036
```

This removes the need for a hard-coded public-agent factory block every time a new counterfactual ranker revision is added.

## Audit focus

rev0036 checks:

```text
adaptive counterfactual summary exists
adaptive branch C++ mismatches = 0
adaptive branch skipped C++ events = 0
branch terminal games > 0
promotion gate passed
statistical gate passed
replay samples passed
new generic rev0036 public-agent aliases load
required docs/scripts/tests exist
```
