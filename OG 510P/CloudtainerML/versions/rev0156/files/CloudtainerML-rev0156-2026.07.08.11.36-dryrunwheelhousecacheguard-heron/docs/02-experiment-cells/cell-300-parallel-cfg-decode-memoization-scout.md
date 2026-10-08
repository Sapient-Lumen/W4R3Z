# CELL-300 — Parallel CFG Decode Memoization Scout

Priority: **P2**  
Status: `future-candidate`

## Cheap first run
Future parser/memoization C++ toy for compatible subset commit; not built in rev0028.

## Metrics
- validation_time
- memo_hit_rate
- parallel_commit_rate
- correctness

## Required baselines
- sequential CFG check
- DFA check
- memoized check

## Stop condition
Drop if it becomes too far from architecture/performance core.
