# ADR-0022: Use RFC 8785 JCS for canonical JSON hashing (proposed)

- Status: proposed
- Date: 2026-02-23

## Decision
DeriveBSD uses RFC 8785 JCS canonicalization for all hashed JSON artifacts (Spec/Lock/Plan/manifests/policy contexts).

## Consequences
- all producers must emit I-JSON compatible values
- schema validation becomes a prerequisite for hashing
- simplifies multi-language tooling interoperability
