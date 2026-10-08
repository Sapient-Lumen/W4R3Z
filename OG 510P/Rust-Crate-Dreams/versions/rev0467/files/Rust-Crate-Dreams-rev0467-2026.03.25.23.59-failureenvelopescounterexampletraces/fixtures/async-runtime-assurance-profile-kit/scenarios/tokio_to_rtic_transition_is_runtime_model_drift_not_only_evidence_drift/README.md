# Scenario: Tokio to RTIC transition is runtime-model drift, not only evidence drift

A robotics/control subsystem moves from a hosted Tokio service loop to an RTIC-based target lane.
Even if both revisions keep roughly the same user-visible feature set, the runtime/concurrency model changed materially.

The diff report should classify that as a runtime-model and support-meaning change, not as a minor evidence update.
