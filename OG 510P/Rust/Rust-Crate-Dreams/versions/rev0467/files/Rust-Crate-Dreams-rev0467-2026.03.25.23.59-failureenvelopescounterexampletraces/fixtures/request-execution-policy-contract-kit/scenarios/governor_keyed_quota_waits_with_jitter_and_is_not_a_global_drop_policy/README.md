# Scenario — governor keyed quota waits with jitter and is not a global drop policy

This scenario captures a keyed `governor` quota with wait-based admission.
The point is to keep per-key scope, wait posture, and jitter visible instead of flattening them into “rate limited”.
