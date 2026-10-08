# Scenario: Tokio `oneshot::Sender` stores one value, but the sender only gets close signals

This scenario exists to prove that sender-visible follow-up evidence can remain weaker than actual consumption.

Current docs say a sent value may remain in the channel until the receiver is dropped, and the sender can observe channel closure with `poll_closed` / `is_closed`.

The fixture should fail any classifier that turns close notification into proof that the receiver awaited and used the value.
