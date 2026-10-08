# Scenario: check then build in the same workspace

Purpose:
- prove that the crate can talk about **workflow-role drift** without pretending Cargo exposed a perfect invalidation proof.

Expected output shape:
- `unit-rebuilds.json` should classify the main story as `tool_invocation_drift_possible`
- `fingerprint-delta.json` should point at the changed command role
- the bundle should stay useful even with no imported nightly Cargo session
