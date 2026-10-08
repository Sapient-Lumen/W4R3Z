# rev0026 C++ shadow rollout results

Run command:

```bash
PYTHONPATH=. python scripts/run_rev0026_cpp_shadow_rollout.py
```

Summary:

```text
strategies: 6
games: 144
C++ transition events: 42,458
C++ skipped events: 0
C++ mismatches: 0
Python rollout errors: 0
replay samples: 8 / 8 passed
promotion gate: passed
statistical gate: passed
truncations: 3
```

Top raw smoke standings:

```text
code_jace60            mean score 0.6667
outcome_counter_wall   mean score 0.5833
pub_counter_wall       mean score 0.5625
pub_threat_overlord    mean score 0.5000
```

The truncation count means draw-half score remains reporting-only for those games.  The value of this run is not the standings; it is the combined gate:

```text
public payoff rows + replay samples + statistical labels + C++ shadow parity
```
