# In-Place Initialization Adoption Kit fixtures

This fixture pack captures the receiver-facing review objects for **P-0447 In-Place Initialization Adoption Kit**.

Core schemas:
- `placement-topology.receipt.schema.json`
- `constructor-lane.report.schema.json`
- `address-commit.receipt.schema.json`
- `failure-cleanup.report.schema.json`
- `init-transition.diff.schema.json`
- `init-support-bundle.manifest.schema.json`

Scenario families cover:
- large heap values that may still be stack-bounced,
- C out-pointer construction that must pin immediately,
- C++ constructor lanes that are not Rust memcpy moves,
- embedded pinned fields with distinct inner/outer commit moments,
- caller-provided storage for async/dyn-style returns,
- release drift when constructor families change.
