# rev0033 experiment matrix additions

New experiment axis:

```text
gameplay action label source
  imitation
  outcome-weighted chosen actions
  branch counterfactual values for all manageable legal actions
```

New artifacts:

```text
data/rev0033_action_counterfactual_candidates.csv
data/rev0033_action_counterfactual_branch_games.csv
data/rev0033_action_counterfactual_cpp_transitions.csv
data/rev0033_counterfactual_action_ranker_model.json
data/rev0033_counterfactual_ranker_games.csv
data/rev0033_counterfactual_ranker_standings.csv
data/rev0033_counterfactual_ranker_cpp_transitions.csv
```

Questions enabled:

```text
When a public policy chooses a move, how often was that move branch-best?
Which action kinds have high counterfactual regret?
Are branch labels stable under more rollout seeds?
Does a counterfactual-trained ranker beat outcome-weighted behavior cloning?
Which high-action-count frames should be budgeted rather than skipped?
```
