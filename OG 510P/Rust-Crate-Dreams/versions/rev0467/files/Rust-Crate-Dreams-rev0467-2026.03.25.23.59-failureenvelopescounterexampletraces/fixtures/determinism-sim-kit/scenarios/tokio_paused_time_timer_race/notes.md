# Scenario: tokio_paused_time_timer_race

This scenario exists to show the smallest honest `simrun` story:

- the backend is **Tokio paused time**,
- the deterministic claim is limited to **single-thread scheduling + virtual time**,
- there is **no simulated network lane**,
- and replay is exact only within that backend/profile.

The point is not that Tokio already solves deterministic simulation by itself.
The point is that a good kit can turn this partial substrate into a compact, reviewable artifact.
