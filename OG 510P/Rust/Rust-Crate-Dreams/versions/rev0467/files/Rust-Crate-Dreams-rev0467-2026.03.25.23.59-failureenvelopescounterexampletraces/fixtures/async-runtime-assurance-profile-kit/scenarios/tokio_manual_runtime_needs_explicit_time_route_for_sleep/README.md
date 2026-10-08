# Scenario: Tokio manual runtime needs an explicit time route for `sleep`

This scenario exists to stop a common flattening move:

> “We use Tokio, therefore time-based async capabilities are available.”

Tokio's current docs say something narrower.
A hand-configured runtime has no resource drivers enabled by default, and time types fail unless the time driver is enabled.
The example receipt keeps the missing activation route explicit instead of silently upgrading the capability claim.
