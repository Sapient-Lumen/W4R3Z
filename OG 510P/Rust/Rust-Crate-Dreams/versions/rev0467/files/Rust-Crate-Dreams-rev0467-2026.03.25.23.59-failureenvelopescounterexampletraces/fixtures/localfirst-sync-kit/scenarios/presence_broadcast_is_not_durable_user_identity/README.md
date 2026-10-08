# Scenario — presence broadcast is not durable user identity

This scenario exists because local-first stacks increasingly expose session-level collaboration signals such as cursor positions, awareness payloads, or live peer metadata.

Those signals may be useful, but they must not be over-claimed as:

- durable synced document state,
- persisted support-bundle material,
- or strong user identity.

The example receipt therefore records a conservative shape:

- delivery is best-effort,
- persistence is none,
- identity is a runtime peer/session identifier,
- and exported bundles default to redacted summaries only.
