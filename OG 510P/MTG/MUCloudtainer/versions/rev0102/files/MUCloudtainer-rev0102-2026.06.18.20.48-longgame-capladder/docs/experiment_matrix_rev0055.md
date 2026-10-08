# rev0055 experiment matrix

| Axis | Setting |
|---|---|
| Target | `cf34_counter_wall` |
| Opponent | `pub_threat_overlord` |
| Life totals | 20, 40 |
| Deck/pilot/mulligan bundle | unchanged from terminal-clean yield panel |
| Target seats | p0 and p1 |
| Starting player | 0 and 1 |
| Reps | 32 per life/seat/starter |
| Max decisions | 900 |
| Truncation policy | terminal-clean required |
| C++ role | transition shadow and replay trace check |
| Claim unit | target/opponent/life cell |

Outputs include current-only cell rows, cumulative-with-rev0054 cell rows, dimensions by seat/start, replay traces, and C++ transition rows.
