# Scenario: Tokio `oneshot` is single-use transfer, not subscription

This scenario exists to prove that some delivery surfaces are not ongoing message media at all.

Current docs say a one-shot channel sends a single message between asynchronous tasks and is created as one sender / one receiver pair.

The fixture should fail any classifier that turns this into reusable queue semantics, broadcast fanout, or cloneable-latest-state observation.
