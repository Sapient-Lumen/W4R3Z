# ADR-0020: Unify artifact targets under one framework (proposed)

- Status: proposed
- Date: 2026-02-23

## Decision
DeriveBSD defines one target abstraction across host/microVM/unikernel/wasm to avoid ad-hoc special cases.

## Consequences
- backends must implement deterministic mapping + conformance tests
- policy can operate uniformly across target kinds
