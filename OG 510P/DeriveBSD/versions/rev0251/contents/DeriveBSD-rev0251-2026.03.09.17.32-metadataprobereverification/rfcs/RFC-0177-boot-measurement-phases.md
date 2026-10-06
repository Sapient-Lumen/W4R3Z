# RFC-0177: Boot measurement phases (PCR separation)

Status: Draft

## Problem

Measured boot is often too brittle for operations:
- a single PCR value encodes "everything" and is hard to interpret
- debuggability suffers
- secrets/admission cannot be gated on clear milestones

## Proposal

1) Define a canonical DeriveBSD **phase vocabulary** for measured boot.

2) Encourage extending a dedicated PCR with literal phase markers.

3) Extend `attestation.reference` with optional `phase_measurement` hints:
- which PCR index and bank are used for phases
- which phase strings must be present for a host role

4) Verifiers should surface phase-related failures via stable reason codes:
- `PHASE_MARKER_MISSING`
- `PHASE_MARKER_OUT_OF_ORDER`

## Why this fits DeriveBSD

- It makes attestation **explainable**.
- It composes with boot assessment + A/B rollback semantics.
- It is implementable on BSD without importing Linux services.

## Open questions

- Do we need a standalone evidence object for phase events, or is the boot event log + receipt reasons sufficient?
- Which PCR should DeriveBSD standardize on (platform-specific)?

