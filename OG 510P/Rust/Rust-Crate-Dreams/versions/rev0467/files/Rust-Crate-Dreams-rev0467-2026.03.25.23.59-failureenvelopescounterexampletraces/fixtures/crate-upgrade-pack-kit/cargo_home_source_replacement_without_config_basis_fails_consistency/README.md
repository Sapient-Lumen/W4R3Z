# Scenario — user-home source replacement is in play but no config-basis receipt was captured

This scenario freezes a contradiction the pack should reject:

- capture/import evidence came from a lane influenced by a user-local Cargo home config,
- but the bundle never records that hidden config basis or override surface.

The pack should fail consistency rather than let a personal source replacement masquerade as the reviewed default lane.
