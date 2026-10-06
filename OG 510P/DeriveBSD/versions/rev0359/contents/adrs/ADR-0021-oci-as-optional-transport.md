# ADR-0021: OCI is optional transport, not identity (proposed)

- Status: proposed
- Date: 2026-02-23

## Decision
OCI Image/Distribution specs may be used as an optional transport for DeriveBSD artifacts, but DeriveBSD digests/signatures/attestations remain authoritative.

## Consequences
- improves adoption in OCI-heavy environments
- avoids “OCI is the store” coupling
