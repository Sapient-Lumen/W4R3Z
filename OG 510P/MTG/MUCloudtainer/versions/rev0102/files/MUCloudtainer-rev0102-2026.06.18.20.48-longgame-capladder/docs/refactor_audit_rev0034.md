# rev0034 refactor/audit

## Refactor

`ranker_policy.py` now has a generic counterfactual-ranker loader:

```python
counterfactual_ranker_model_path(revision)
load_counterfactual_ranker_agent(revision)
load_blended_counterfactual_ranker_agent(revision, profile)
```

This avoids copy-pasting a new loader for every action-counterfactual label-budget revision.  Existing rev0033 names still work.

`public_agents.py` now recognizes the rev0034 counterfactual ranker names:

```text
counterfactual_linear_ranker_rev0034
counterfactual_ranker_blend_threat_rev0034
counterfactual_ranker_blend_counter_rev0034
counterfactual_ranker_blend_patient_rev0034
```

`action_counterfactual.py` now emits per-action and per-situation label-noise fields.

## Audit checks

The rev0034 audit checks:

```text
scaled counterfactual collection row counts
branch rollout count per action
zero C++ branch mismatches/skips
label-audit fields present
rev0034 model loads with the public feature contract
rev0034 public-agent factory names work
promotion/statistical/replay/C++ gates pass for evaluation payoff
required docs/scripts/tests/data exist
```
