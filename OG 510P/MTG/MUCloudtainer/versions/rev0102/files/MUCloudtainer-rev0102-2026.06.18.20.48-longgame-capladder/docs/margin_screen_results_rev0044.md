# rev0044 margin-screen results

Archived artifacts:

```text
data/rev0044_margin_screen_model.json
data/rev0044_margin_screen_holdout_eval.csv
data/rev0044_margin_screen_pool.csv
data/rev0044_margin_online_racing_selected.csv
data/rev0044_margin_online_racing_candidates.csv
data/rev0044_margin_online_racing_branch_games.csv
data/rev0044_margin_online_racing_allocations.csv
data/rev0044_margin_online_racing_votes.csv
data/rev0044_margin_online_racing_cpp_transitions.csv
data/rev0044_margin_online_racing_situation_summary.csv
data/rev0044_margin_screen_racing_summary.json
```

Smoke result from the archived run:

```text
historical source situations:      84
model train rows:                  59
model holdout rows:                25
holdout RMSE:                      ~0.444
holdout top-quartile decisive:     0.50
holdout baseline decisive:         0.44

selected hard situations:          10
candidate action rows:             50
branch games:                      90
adaptive extra rollouts:           40
branch truncations:                0
C++ checked transitions:           13,262
C++ skipped transitions:           0
C++ mismatches:                    0
decisive situations:               1
decisive labels per 100 rollouts:  ~1.11
```

Interpretation: the model has a weak but measurable holdout enrichment signal. The live branch labels were still sparse. This is not a promoted policy result. It is a label-budget instrumentation result.

The next step should compare this margin-screen queue against the previous hard-frame queue on matched situations, then use the better queue for larger action-counterfactual collection.
