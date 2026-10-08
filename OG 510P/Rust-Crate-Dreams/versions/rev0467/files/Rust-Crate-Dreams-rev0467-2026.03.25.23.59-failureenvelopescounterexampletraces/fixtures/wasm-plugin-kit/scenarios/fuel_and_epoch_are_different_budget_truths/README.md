# Scenario: fuel and epochs are different execution-budget truths

This scenario exists because Wasmtime documents that:

- fuel-based interruption is deterministic,
- epoch-based interruption is usually faster,
- and host-side timeout semantics are not the same thing as guest-instruction budgeting.

A worthy plugin contract should therefore report *which* budget basis is in force instead of merely saying “has a timeout”.

