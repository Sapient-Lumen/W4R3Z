# Scenario: Tokio `mpsc` has a fixed receiver cohort

This scenario exists to prove that some surfaces do not admit late-joining receivers at all.

Current docs describe Tokio `mpsc` as a multi-producer, single-consumer queue with separate sender and receiver handles returned by channel creation.

The fixture should fail any classifier that invents a late subscribe or clone-receiver route.
