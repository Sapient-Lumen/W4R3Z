# rev0031 experiment matrix additions

New axes added this revision:

| Axis | Values | Purpose |
|---|---|---|
| C++ segment parity | pass/fail per forced segment | Does C++ preserve state across no-choice runs? |
| Segment length | 1..28 in smoke run | Estimate future batching benefit. |
| Repeated branch rollouts | 3 per branch | Reduce keep-vs-mulligan label noise. |
| Opening pairs | 36 paired situations | Increase counterfactual label budget. |

New generated files:

```text
data/rev0031_cpp_segment_games.csv
data/rev0031_cpp_segment_rows.csv
data/rev0031_cpp_segment_summary.json
data/rev0031_repeated_cf_scale_branch_games.csv
data/rev0031_repeated_cf_scale_pairs.csv
data/rev0031_repeated_cf_scale_cpp_transitions.csv
data/rev0031_repeated_cf_scale_summary.json
```
