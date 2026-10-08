# Experiment matrix — rev0070

| Experiment | Purpose | Status | Key output |
|---|---|---:|---|
| Population precision gate | Replicate the 2×3 counter/threat population frontier with preregistered min games and conservative lower-bound floors. | Complete, not promotable | `data/rev0070_population_precision_summary.json` |
| Sampled C++ shadow | Check an even transition sample from the replicated run without shipping or checking every transition. | Passed | `data/rev0070_population_precision_cpp_transition_sample.csv` |
| Evidence active/historical split | Separate executable/doc raw-path blockers from generated historical data mentions. | Complete | `data/rev0070_evidence_index.json` |
| Semantic matrix completeness | Treat empty scores and zero-game rows as incomplete, not as neutral values. | Tested | `tests/test_rev0070_population_precision.py` |
