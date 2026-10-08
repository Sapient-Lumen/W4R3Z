# Scenario: Flume `send` success requires a live receiver but still is not processing receipt

This scenario exists to prove that non-Tokio channel families share the same gap: liveness-gated success is still not proof of observation or processing.

Current docs say `send` / `send_async` return an error if all receivers have been dropped. Bounded channels may wait for capacity; unbounded channels do not block.

The fixture should fail any classifier that turns success into proof that some receiver handled the message.
