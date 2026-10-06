# ADR-0235: Attestation-consuming action receipts pin the exact decision tuple

Status: Accepted  
Date: 2026-03-21

## Context

`ADR-0082` already fixed the high-level boundary:

- `attestation.receipt` is verifier evidence only,
- `attestation.admission.policy` maps actions to `attestation.requirement`,
- and authoritative action receipts can summarize what attestation decision they consumed.

The archive also now fixes several adjacent ambiguities:

- `attestation.reference` authoring is cohort-shaped and replay-first by default,
- non-baseline references are explicit timeboxed exceptions,
- renewed exceptions are digest-linked successor artifacts,
- reference selection is exact-digest-pinned,
- and attestation receipts that name an AK now carry exact attester-identity provenance by digest.

What still remained too soft was the **consuming action-side join**.

Today, an authoritative action receipt such as:

- `secret-receipt`,
- `breakglass-receipt`, or
- `workload-identity-issue-receipt`

could say `attestation_verification.decision = accepted` while still leaving one or more of the decisive attestation inputs implicit.
That leaves room for several expensive implementation drifts:

- an action receipt cites a verifier result but not the requirement that made it acceptable,
- an action receipt cites a requirement but not the concrete verifier result actually consumed,
- or an action receipt depends on a policy service/database to recover which attestation-admission policy rule was in force.

That is exactly how service logs, control-plane databases, or dashboard state become the real product truth.

## Decision

**Whenever an authoritative action receipt records a decisive attestation outcome (`accepted`, `degraded`, or `rejected`), it must pin the full exact decision tuple.**

That tuple is:

1. `attestation_requirement_digest`
2. `attestation_receipt_digest`
3. `attestation_admission_policy_digest`

This applies to the canonical v0 consuming authority receipts:

- `secret-receipt`
- `breakglass-receipt`
- `workload-identity-issue-receipt`

More specifically:

1. `attestation_verification.decision` remains the compact action-side summary.
2. If the decision is `accepted`, `degraded`, or `rejected`, then all three exact digests above are required.
3. The digest tuple is the portable answer to **which requirement, which verifier result, and which gate policy materially participated in this authority decision**.
4. Backend policy engines, registries, or control-plane databases may still exist as implementation detail, but they do not become the archive truth.

## Consequences

### Positive

- Secret release, breakglass, and workload identity issuance now stay replayable without relying on side databases.
- Incident/support/export flows can explain a sensitive authority decision from portable artifacts instead of dashboard archaeology.
- Future implementation work has a crisp target: compile policy and verification into authoritative receipts, not into mutable service memory.

### Trade-offs

- Consuming action receipts become slightly stricter when they claim attestation materially participated.
- Implementations must persist the exact requirement/policy digests they actually used instead of reconstructing them later.

## Alternatives considered

- **Keep the digests optional.** Rejected: that leaves the archive dependent on backend/private state for the decisive join.
- **Require only the receipt digest.** Rejected: that still leaves policy/requirement truth implicit.
- **Duplicate the full attestation receipt inside every authority receipt.** Rejected: too heavy; digest-bound joins already exist.

## Implementation notes

Accepted and wired through the consuming authority receipt schemas/examples, `docs/492-attestation-results-evidence-and-admission-issue-boundary.md`, the adjacent attestation/admission/profile docs, and `tools/check_attestation_action_verification_contract.py`.
