# Scenario: glommio `spawn_local` requires a current single-thread executor

This scenario proves that thread-local execution support can include stricter per-thread executor assumptions.

The important facts are:
- Glommio is a thread-per-core, thread-local I/O model;
- `spawn_local` panics unless called from a `LocalExecutor`;
- and Glommio’s locality story includes single-thread executor / placement discipline rather than generic runtime portability.
