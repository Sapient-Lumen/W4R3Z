# Benchmark evaluation stop rule

`OQ-0109` blocks benchmark, leaderboard, SOTA, hidden-test, validation-suite, challenge, or independent-evaluation language unless benchmark-suite, benchmark-metric, and evaluation-protocol rows are declared and current.

Forbidden move: `benchmark pass + metric improvement + replayable evaluation = route promotion`.

Permitted move: benchmark rows may cap, freeze, demote, or rollback route-local wording when leakage, Goodhart pressure, adaptive reuse, metric proxy failure, or evaluation-protocol failure appears.
