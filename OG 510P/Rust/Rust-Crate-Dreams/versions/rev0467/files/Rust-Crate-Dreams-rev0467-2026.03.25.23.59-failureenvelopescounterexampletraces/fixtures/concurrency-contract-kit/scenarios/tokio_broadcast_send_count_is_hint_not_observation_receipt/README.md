# Scenario: Tokio `broadcast::Sender::send` count is a hint, not an observation receipt

This scenario exists to prove that a returned receiver count is not the same thing as proof that those receivers actually observed the sent value.

Current docs say successful send requires at least one active receiver, and `receiver_count()` explicitly says the sent message is not guaranteed to reach that many receivers.

The fixture should fail any classifier that turns active-receiver count into delivery proof.
