# rev0037 experiment matrix

| Axis | rev0037 setting | Purpose |
|---|---:|---|
| Label audit | fixed_equal vs adaptive_race | Compare label allocation methods on matched situations |
| Fixed rollouts/action | 3 | Conservative equal-budget label baseline |
| Adaptive base rollouts/action | 1 | Cheap first pass over every selected action |
| Adaptive extra budget | per-situation derived from fixed budget | Spend saved budget on top contenders |
| Sampled situations | 12 | Smoke-scale label audit |
| Branch rollouts | 81 total branch games | Shared branch-outcome matrix |
| C++ branch shadow | 20,358 transitions | Parity check label traffic |
| Segment benchmark games | 48 | Compare C++ segment vs one-action transport |
| Segment forced actions | 8,415 | Benchmark no-choice segment traffic |

The matrix remains smoke-scale.  Rows are designed to exercise the infrastructure, not to make strategic claims about MUC-5.
