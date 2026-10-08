# rev0049 results note

Expected generated artifacts:

```text
data/rev0049_yield_online_candidates.csv
data/rev0049_counterfactual_action_ranker_model.json
data/rev0049_terminal_clean_yield_games.csv
data/rev0049_terminal_clean_yield_summary.json
```

Read this revision as an evaluation-contract improvement.  A terminal-clean
payoff table is cleaner than a truncation-heavy smoke table, but the table is
still small and should not be treated as final MUC theory.

The result to watch is:

```text
terminal_clean_summary.terminal_clean == true
promotion.passed == true
statistical_gate.passed == true
cpp_shadow_summary.mismatches == 0
```
