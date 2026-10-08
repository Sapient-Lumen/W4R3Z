# Scenario: agent-backed X.509 source and static dev identity must not share rotation claims

This scenario protects one easy lie:

> “both environments use SPIFFE identities, so both support live rotation.”

The live agent-backed X.509 path should publish a `workload_api_live_x509` identity source with watch-driven rotation and updated-material claims for new handshakes.
A static dev identity may still be useful, but it must not inherit live-rotation language.
