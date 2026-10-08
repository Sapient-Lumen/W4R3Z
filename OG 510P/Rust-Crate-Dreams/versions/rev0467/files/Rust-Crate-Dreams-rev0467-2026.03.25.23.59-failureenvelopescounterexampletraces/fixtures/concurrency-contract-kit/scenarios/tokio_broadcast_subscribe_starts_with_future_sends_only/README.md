# Scenario: Tokio `broadcast::Sender::subscribe` starts with future sends only

This scenario exists to prove that a late-joining broadcast receiver is admitted by an explicit subscribe route, but does not inherit values that were sent before the subscription call.

Current docs say the returned receiver will receive values sent after the call to `subscribe`.

The fixture should fail any classifier that turns this into current-snapshot subscribe, replay-from-origin, or shared-existing-backlog semantics.
