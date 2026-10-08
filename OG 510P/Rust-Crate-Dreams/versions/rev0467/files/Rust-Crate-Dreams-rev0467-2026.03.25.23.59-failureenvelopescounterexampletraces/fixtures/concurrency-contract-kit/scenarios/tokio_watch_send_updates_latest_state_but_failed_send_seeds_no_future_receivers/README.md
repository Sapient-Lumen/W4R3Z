# Scenario: Tokio `watch::Sender::send` updates latest state when open, but failed send seeds no future receivers

This scenario exists to prove that acceptance semantics include both a success meaning and a failure ceiling.

Current docs say successful send replaces the current value and notifies receivers, while failed send returns the value and does not make it available for future receivers.

The fixture should fail any classifier that treats failed send as if it had still updated the shared state.
