# SQLite metrics through rev0011

SQLite is the local metrics spine for MTGSim. It keeps timing and result history close to the cube without requiring a service.

## What is stored

- Harness step durations and statuses.
- GCC build target timing.
- C++ case timing and status.
- Scenario timing and assertion counts.
- Fuzz seed timing, action counts, invariant checks, and trigger-stack action counts.
- Rule progress snapshots.
- Card catalog build reports.

## Why this matters

Long-term testing needs high parallelization and continuous optimization. Duration-greedy sharding depends on historical timings, and a local SQLite DB is enough to support that without adding infrastructure.

## Current caution

The metrics DB is a local generated artifact. It is useful in the working tree and reports, but package auditing flags large generated files for review so shared datacubes do not silently bloat.
