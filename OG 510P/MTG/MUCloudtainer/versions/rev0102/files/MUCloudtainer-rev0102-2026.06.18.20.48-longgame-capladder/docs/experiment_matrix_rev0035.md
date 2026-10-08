# rev0035 experiment matrix additions

New axis:

```text
action-counterfactual label mode
  full_menu_only
  budgeted_high_action_subset
  future: adaptive_branch_racing
```

New artifacts:

```text
data/rev0035_action_counterfactual_candidates.csv
data/rev0035_action_counterfactual_branch_games.csv
data/rev0035_action_counterfactual_cpp_transitions.csv
data/rev0035_counterfactual_action_ranker_model.json
data/rev0035_budgeted_counterfactual_ranker_games.csv
data/rev0035_budgeted_counterfactual_ranker_summary.json
```

Key comparison to run later:

```text
rev0034 full-menu capped labels
vs
rev0035 budgeted high-action labels
vs
future adaptive branch racing labels
```

Evaluation guardrails stay unchanged:

```text
public DecisionFrame only
split transition/agent RNG
promotion gate
statistical gate
replay samples
C++ shadow parity
truncation warnings separated from reward
```
