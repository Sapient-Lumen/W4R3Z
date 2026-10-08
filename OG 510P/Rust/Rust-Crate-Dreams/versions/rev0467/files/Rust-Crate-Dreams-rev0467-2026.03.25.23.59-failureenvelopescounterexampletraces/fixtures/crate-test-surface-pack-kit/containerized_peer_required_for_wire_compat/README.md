# Scenario family — containerized peer is optional for fast tests but required for wire compatibility

This fixture family exists for crates where most downstream tests can run in-process or against loopback fakes, but protocol fidelity or database-wire compatibility requires a real peer.

It is meant to catch support drift such as:

- documentation implying everything is covered by fast local fixtures,
- CI silently depending on Docker for the most important compatibility witness,
- or a crate claiming `containerized_dependency` is optional without marking which scenarios actually require it.

A good test-surface pack should make four things explicit:

1. which scenarios are covered by in-process or loopback topology,
2. which scenarios require a containerized peer,
3. what host capabilities are assumed (for example Docker daemon or loopback networking),
4. and whether the wire-compat scenario is officially supported or manual-review-only.

This family keeps “fast local test ergonomics” separate from “full fidelity of a real peer”.
