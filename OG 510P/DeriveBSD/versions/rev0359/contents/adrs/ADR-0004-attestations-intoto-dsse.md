# ADR-0004: Provenance attestations use in-toto + DSSE

- Status: proposed
- Date: 2026-02-25

## Context

DeriveBSD needs a **portable, ecosystem-compatible** container for signed statements about:
- what was built (artifact digests)
- from which inputs (spec/lock/plan digests)
- under which environment (toolchain, platform posture)
- and which policy gates were applied (tests, vuln checks, approvals)

We also want attestations to be composable (SBOM, VEX, test receipts, provenance) and easy to verify with existing tooling.

References:
- in-toto specs index (Attestation Framework + core spec): https://in-toto.io/docs/specs/
- in-toto Attestation Framework v1 (Statement/Envelope): https://github.com/in-toto/attestation

## Decision

Use an **in-toto Statement** wrapped in a **DSSE envelope** as the baseline attestation container format.

### 1) Envelope

- The signed envelope is the verification unit.
- The payload is canonicalized and typed.
- Envelope metadata (signatures, key ids) is preserved as evidence.

### 2) Statement payload

- Statement identifies the **subject** (artifact digest(s)).
- Statement `predicateType` selects a well-known predicate (e.g., provenance).
- Predicates are where DeriveBSD carries typed pointers to:
  - Spec/Lock/Plan digests
  - build sandbox profile digest (promise profile)
  - toolchain trust tier / DDC receipts (optional)
  - policy decision record digests

## Consequences

- Interop: we can consume and emit attestations compatible with the broader in-toto / Sigstore ecosystem.
- Extensibility: new predicate types can be introduced without changing the envelope.
- Evidence spine integration: attestation verification results become structured evidence that can be bundled and explained.

