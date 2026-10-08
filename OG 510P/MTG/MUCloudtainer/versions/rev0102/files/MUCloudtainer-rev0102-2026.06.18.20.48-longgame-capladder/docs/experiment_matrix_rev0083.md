# rev0083 experiment matrix

| Item | Value |
|---|---:|
| Selected cell | `counter40_vs_threat40`, life 20, closure threat |
| Counter policies | 3 |
| Threat policies | 1 |
| Target seats | 2 |
| Starting players | 2 |
| Reps per seat/start/policy | 16 |
| Total games | 192 |
| Terminal-clean games | 192 |
| Truncations | 0 |
| C++ supported transitions checked | 12,000 |
| C++ mismatches | 0 |
| Broad-pool eligible | no |

| Counter policy | Games | Mean score | Familywise LCB | Familywise UCB |
|---|---:|---:|---:|---:|
| `legacy_cf34_counter_ranker` | 64 | 0.171875 | 0.0 | 0.3652716888 |
| `public_counter_guard` | 64 | 0.53125 | 0.3378533112 | 0.7246466888 |
| `public_counter_life20_stabilizer` | 64 | 0.53125 | 0.3378533112 | 0.7246466888 |

Paired guard-vs-candidate outcome comparison: 58 same-score cells, 3 candidate-better cells, 3 guard-better cells.
