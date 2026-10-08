# rev0021 experiment matrix additions

| Axis | New value | Why it matters |
|---|---|---|
| C++ seam | batched trace transitions | Measures C++ executable throughput separately from Python replay/projection |
| Policy type | `linear_ranker_rev0021` | First learned-ish public policy wrapper |
| Training mode | supervised imitation | Lower-risk bridge before RL/search |
| Model artifact | JSON coefficients | Inspectable and pickle-free |
| Gate | promotion + statistical + replay | Same comparison standard as code/public baselines |

New commands:

```bash
PYTHONPATH=. python scripts/benchmark_rev0021_cpp_trace_batch.py
PYTHONPATH=. python scripts/run_rev0021_ranker_policy_eval.py
PYTHONPATH=. python scripts/audit_cube.py
```
