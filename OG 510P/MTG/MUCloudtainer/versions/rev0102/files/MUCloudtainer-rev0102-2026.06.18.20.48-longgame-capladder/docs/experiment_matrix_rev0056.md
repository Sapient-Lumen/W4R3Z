# Experiment matrix update — rev0056

| Axis | Setting |
|---|---|
| Target | `cf34_counter_wall` |
| Opponent | `pub_threat_overlord` |
| Life totals | 20 and 40, treated as separate cells |
| Reps | 24 per life / target-seat / starting-player cell |
| Max decisions | 900 |
| Truncation policy | zero tolerated for claim rows |
| C++ role | transition shadow and replay trace parity |
| Claim type | independent life-cell holdout replication |

The holdout schedule is intentionally narrower than a population table. It is designed to ask whether a specific cell-level claim survives seed-disjoint repetition.
