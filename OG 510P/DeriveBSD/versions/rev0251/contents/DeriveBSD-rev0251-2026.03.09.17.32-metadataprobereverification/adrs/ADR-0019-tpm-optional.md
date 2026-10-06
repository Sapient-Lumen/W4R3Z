# ADR-0019: TPM features are optional; policy-gated (proposed)

- Status: proposed
- Date: 2026-02-23

## Decision
DeriveBSD treats TPM/attestation/sealed-secret features as optional and policy-gated.
Baseline DeriveBSD does not depend on TPM availability.

## Consequences
- supports airgapped/offline and commodity deployments
- enables “high assurance zones” to require stronger host identity later
