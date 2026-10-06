# ADR-0229: Incident bundles carry attestation proof by digest

Date: 2026-03-21
Status: Accepted

## Context

DeriveBSD already treats measured posture as typed evidence instead of a verifier side channel.
`docs/226-platform-posture-and-attestation-results-as-evidence.md` already established the attestation lane:

- `boot.attestation` records the exact measured-boot evidence,
- `attestation.reference` records the verifier/reference scope used to judge that evidence,
- and `attestation.receipt` records the verifier's time-bounded judgment.

The official incident/support-bundle contract still lagged behind that design in practice.
`incident.bundle` already had metadata fields for `boot_attestation_digest`, `attestation_reference_digest`, and `attestation_receipt_digests`, but the archive still did not treat them as an explicit official support-handoff lane, and canonical `bundle.plan` examples could not request them through shared include knobs.

That omission is expensive because it blurs three distinct questions:

- what exact measured-boot evidence did the host produce,
- what reference scope/policy did the verifier compare it against,
- and what exact verifier judgment materially participated in the incident.

Without an explicit join, support falls back to verifier dashboards, portal screenshots, or ticket prose instead of typed answers about exact measured posture.

## Decision

**Incident/support bundles may carry attestation posture proof by typed digest join.**

1. **Make the attestation triad explicit on the official support-handoff lane.**
   - `boot_attestation_digest` identifies the exact `boot.attestation` evidence carried by the bundle.
   - `attestation_reference_digest` identifies the exact `attestation.reference` scope/policy carried by the bundle.
   - `attestation_receipt_digests` identify the exact `attestation.receipt` verifier judgments carried by the bundle.

2. **Make bundle planning explicit too.**
   - `incident.bundle` include knobs now expose `boot_attestation`, `attestation_reference`, and `attestation_receipts`.
   - Because `bundle.plan.selection.include` reuses that shared include surface, support-bundle planning can now request the attestation lane deliberately instead of relying on prose.

3. **Keep evidence, reference scope, and verdict distinct.**
   - This ADR does not collapse measured posture into one generic verifier-debug field.
   - `boot_attestation_digest`, `attestation_reference_digest`, and `attestation_receipt_digests` answer different questions and stay separately explainable.

4. **Keep the routine support lane metadata-first.**
   - This ADR does not bless raw TPM event logs, verifier-private databases, dashboard screenshots, or portal dumps as routine support-bundle truth.
   - Richer replay/debug material can still exist elsewhere; the support-handoff boundary stays digest-first.

5. **Use the lane when measured posture materially shaped the story.**
   - Bundles should include the attestation triad when boot posture, verifier scope, or expiring posture judgments materially participated in admission, secret release, workload identity issuance, or incident interpretation.
   - Bundles do not need to carry every historical attestation artifact.

## Consequences

- Official support handoff can now explain measured posture without teaching responders to trust verifier dashboards or portal screenshots.
- Canonical bundle examples become mechanically checkable instead of placeholder-shaped for the attestation lane.
- The archive keeps a narrow boundary: no new attestation subsystem, no mandatory verifier backend, and no silent promotion of verifier-private output into routine support truth.

## Alternatives considered

- **Leave the attestation lane implicit in prose.** Rejected: the schema already had most of the right fields, but implementers still needed the archive to say they are official support-handoff truth.
- **Carry only `boot_attestation_digest`.** Rejected: measured evidence without the reference scope or verifier judgment is often not enough to explain why another subsystem admitted or denied something.
- **Carry only verifier receipts.** Rejected: verifier verdicts should stay explainable back to exact evidence and reference scope.
- **Add a generic verifier-debug blob.** Rejected for now: it widens the routine handoff contract and fights the archive's typed evidence model.

## Status

Accepted and wired through the canonical bundle examples, the attestation/support-bundle docs, and archive hygiene checks.
