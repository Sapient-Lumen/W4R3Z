# Scenario: Tokio `mpsc` delivers each message to a single consumer

This scenario exists to prove that **single-consumer delivery** is a distinct audience class and should not be flattened into “multiple producers plus async messaging” generality.

Current docs say Tokio `mpsc` is a multi-producer, single-consumer queue.

The fixture should fail any classifier that turns this into MPMC competition, broadcast fanout, or latest-state watch semantics.
