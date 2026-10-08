# rev0079 experiment matrix

| Question | Evidence | Result | Status |
|---|---:|---|---|
| Does the eligible broad pool pass a hierarchical familywise gate? | rev0069+rev0070 complete-panel summaries | 0/12 hierarchical rows passed | blocked |
| Does the global layer still quarantine? | 1 global familywise row | LCB 0.2632; low floor | quarantined |
| Do life strata pass? | 2 by-life rows | 0/2 passed; both low floor | quarantined |
| Do size strata pass precision? | 3 by-size rows | 0/3 passed; all precision_target_not_met | blocked |
| Are fine size/life cells ready to judge? | 6 size/life rows | 0/6 passed; all underpowered_min_games | diagnostic only |
| Does a small 3×3 game still require approximate fictitious play? | support-enumeration diagnostic | exact value 0.5, near-zero gap | refactored |
| Did this revision add bulky raw evidence? | artifact audit | no rev0079 games/transitions/replay traces | compact |
