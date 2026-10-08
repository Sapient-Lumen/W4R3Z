# Scenario — claimed public redaction fails without an exact receipt

This scenario captures a pack that wants to say redaction has already happened, but still lacks a bounded receipt for what changed.

It proves that:
- `redaction_status: applied` must fail consistency when no exact redaction receipt exists,
- a public or candidate-public export posture cannot quietly rely on silent sanitization,
- and public-surface honesty requires the transformation basis to be reviewable, not merely implied.
