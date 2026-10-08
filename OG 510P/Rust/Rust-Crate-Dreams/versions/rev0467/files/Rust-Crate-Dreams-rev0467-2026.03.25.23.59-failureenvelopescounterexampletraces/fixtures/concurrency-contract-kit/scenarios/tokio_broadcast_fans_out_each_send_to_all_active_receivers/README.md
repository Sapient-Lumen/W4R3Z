# Scenario: Tokio `broadcast` fans out each send to all active receivers

This scenario exists to prove that **all active receivers** is a distinct delivery audience and that one receiver consuming a value does not prevent other active receivers from receiving their own clone.

Current docs say each sent value is seen by all consumers / all active receivers in order.

The fixture should fail any classifier that turns this into single-consumer competition, latest-state-only watch semantics, or current-waiter-only notification.
