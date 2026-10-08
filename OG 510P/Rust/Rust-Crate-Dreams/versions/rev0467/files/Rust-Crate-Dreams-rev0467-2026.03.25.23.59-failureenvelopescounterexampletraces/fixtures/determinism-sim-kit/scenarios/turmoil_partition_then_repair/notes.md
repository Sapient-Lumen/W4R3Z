# Scenario: turmoil_partition_then_repair

This scenario exists to show a more interesting multi-host deterministic simulation story:

- the backend is **turmoil**,
- the run is single-thread deterministic and uses seeded network hardship,
- a partition is introduced and later repaired,
- and the minimized replay remains only **profile-compatible**, not globally backend-equivalent.

It also demonstrates why the crate should preserve backend truth instead of pretending every deterministic run means the same thing.
