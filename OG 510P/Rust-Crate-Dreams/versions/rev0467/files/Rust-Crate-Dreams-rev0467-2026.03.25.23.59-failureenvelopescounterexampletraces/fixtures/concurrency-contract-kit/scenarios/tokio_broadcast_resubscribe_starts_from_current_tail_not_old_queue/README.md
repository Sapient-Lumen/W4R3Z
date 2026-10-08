# Scenario: Tokio `broadcast::Receiver::resubscribe` starts from the current tail, not the old queue

This scenario exists to prove that resubscribe is a distinct join-start class.

Current docs say the new receiver starts from the current tail and does not include elements that are in the queue of the current receiver.

The fixture should fail any classifier that turns this into replay-from-origin, inherited-current-queue, or generic future-only subscribe without tail semantics.
