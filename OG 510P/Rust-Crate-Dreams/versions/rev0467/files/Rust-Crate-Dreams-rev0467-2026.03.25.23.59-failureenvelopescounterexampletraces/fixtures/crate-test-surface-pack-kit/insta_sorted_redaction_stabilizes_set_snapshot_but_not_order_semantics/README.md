# Scenario family — sorted redaction stabilizes a set-shaped snapshot, but should not erase order semantics

This fixture family exists for crates that use snapshot tests to show API responses, configs, or diagnostic outputs whose map/set order is otherwise unstable.

It is meant to catch support drift such as:

- using sorting/redaction to make snapshots deterministic without marking the semantic boundary,
- implying a snapshot proves order-insensitive semantics when it only proves stability of rendering,
- or forgetting that some fields still need manual review even after normalization.

A good test-surface pack should keep determinism help separate from semantic proof.
