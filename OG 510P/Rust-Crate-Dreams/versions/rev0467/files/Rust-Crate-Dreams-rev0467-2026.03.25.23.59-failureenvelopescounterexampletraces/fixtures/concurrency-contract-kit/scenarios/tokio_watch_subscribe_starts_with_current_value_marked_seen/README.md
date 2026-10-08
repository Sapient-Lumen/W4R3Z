# Scenario: Tokio `watch::Sender::subscribe` starts with the current value already marked seen

This scenario exists to prove that a late-joining watch receiver begins from the current snapshot rather than from future-only subscribe semantics.

Current docs say the current value at the time the receiver is created is considered seen.

The fixture should fail any classifier that turns this into backlog replay or future-only subscription.
