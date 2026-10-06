# RFC-0161: Platform posture + attestation receipts as evidence

Status: Draft  
Last updated: 2026-02-24

## Motivation

DeriveBSD already defines optional measured boot evidence (`boot.attestation`).
To make posture checks reusable across the system, we need **typed attestation results**
that can be referenced by:
- health-gated updates and change-set gates
- secret grants (credential broker release)
- incident bundles / forensics
- admission control (fleet policies)

Without receipts, posture becomes a one-off integration and loses auditability.

## Proposal

Introduce three new evidence objects:

1) **`attestation.reference`**: content-addressed reference values for a policy scope.  
2) **`attestation.receipt`**: verifier-issued, signed attestation results binding evidence + reference + verdict.  
3) **`attestation.requirement`**: a small gate object describing freshness + minimum verdict requirements.

Add a new change-set step:
- `op: require-attestation`
- references one `attestation.requirement`

Update secret grants to allow:
- `constraints.attestation_requirement_digest`
- `constraints.attestation_receipt_digest`

Update incident bundles to include attestation digests when enabled.

Add a typed journal event:
- `attestation-event` (allOf `event.record`)

## Design notes

- Prefer event-log replay against boot manifests over brittle “golden PCR” policies.
- Receipts must be short-lived (expiry) to support revocation via time.
- Obligations allow a verifier to drive downstream actions without hardcoding policy into clients.
- Keep the lane optional: no mandatory TPM requirement.

## Open questions

- What is the minimum “obligations” vocabulary worth standardizing in v1?
- How should verifier public keys / trust roots be distributed (reuse policy module lane vs dedicated)?
- Should `attestation.reference` be treated as policy (w/ ADRs) or as data (w/ receipts only)?

## Schema references

- `spec/attestation.reference.schema.json`
- `spec/attestation.receipt.schema.json`
- `spec/attestation.requirement.schema.json`
- `spec/attestation.event.schema.json`
