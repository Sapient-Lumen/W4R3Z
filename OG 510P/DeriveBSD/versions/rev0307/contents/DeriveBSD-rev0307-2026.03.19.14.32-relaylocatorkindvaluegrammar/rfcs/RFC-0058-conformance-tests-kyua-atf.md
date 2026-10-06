# RFC-0058: Conformance test harness (Kyua + ATF)

- Status: draft
- Created: 2026-02-23

## Summary
Standardize a test harness and fixture strategy that validates DeriveBSD invariants (schemas, policy purity, build sandboxing, runtime mapping, CLI outputs).

## Goals
- prevent regression into “impure and ad-hoc”
- keep fixtures small and digest-driven
- CI-friendly reporting
