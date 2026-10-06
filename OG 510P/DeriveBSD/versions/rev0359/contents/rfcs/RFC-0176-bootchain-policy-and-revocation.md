# RFC-0176: Bootchain policy and revocation (bootchain.policy)

Status: Draft

## Problem

DeriveBSD needs a **targeted revocation** mechanism for boot-chain components.

Key rotation alone is too blunt:
- it revokes everything signed by a key, not one vulnerable component generation
- it forces emergency re-enrollment paths
- it is difficult to stage/confirm safely

## Proposal

1) Add a new policy object `bootchain.policy` with:
- allow rules for `(vendor_id, component_id)` with minimum allowed `generation`
- optional explicit allowlist of build digests
- explicit revocations for build digests and/or generation ranges

2) Extend `attestation.reference` to include `bootchain_policy_digest`.

3) Extend `incident.bundle` to optionally include referenced `bootchain_policy_digests`.

## Why this fits DeriveBSD

- Policy is data; revocation should be **diffable and reviewable**.
- Boot and attestation already produce evidence; revocation decisions should be **explainable**.
- Works with existing trust stack (TUF/Uptane-inspired metadata + transparency optional lanes).

## Semantics

- A boot-chain is acceptable iff every relevant component satisfies the bootchain policy.
- Violations yield verifier reason codes:
  - `BOOTCHAIN_COMPONENT_REVOKED`
  - `BOOTCHAIN_GENERATION_TOO_OLD`
  - `BOOTCHAIN_BUILD_NOT_ALLOWED`

Receipts should be careful not to leak sensitive device identifiers.

## Rollout

- Treat bootchain policy updates as **confirmable change-sets** (RFC-0174):
  - stage new policy
  - apply to a canary set
  - confirm after observation
  - auto-revert on lockout signals

## Open questions

- Should `bootchain.policy` live under trust policy (TUF metadata) or as an independent policy object?
- How do we represent firmware-provided revocations (UEFI dbx) in a portable way?

## Files

- New: `spec/bootchain.policy.schema.json`
- New example: `spec/examples/bootchain.policy.json`
- Modified: `spec/attestation.reference.schema.json`
- Modified: `spec/incident.bundle.schema.json`, `spec/examples/incident.bundle.json`

