# ADR-0237: Rejected attestation does not silently mint ordinary authority; breakglass stays explicit

- Status: Accepted
- Date: 2026-03-22
- Deciders: DeriveBSD archive maintainers

## Context

Recent archive cuts already fixed several expensive attestation ambiguities:

- authoritative consuming receipts pin the exact requirement/receipt/policy tuple,
- degraded admission stays requirement-shaped,
- and breakglass remains the explicit emergency lane when operators must proceed despite a stricter ordinary rule.

That still leaves one quiet loophole:
**what happens when the consumed attestation decision is `rejected`, but an implementation still wants ordinary secret delivery or workload-identity issuance to succeed?**

Without a narrow answer, implementations will drift toward one or more hidden behaviors:

- secret brokers that log `attestation_verification.decision = rejected` but still hand out the secret,
- workload identity agents that mint a credential anyway and expect operators to infer an override from notes,
- sticky verifier/session state that quietly reuses a prior “good” answer,
- or dashboards/tickets that become the real override mechanism.

Those are exactly the kinds of backend-state folklore this archive has been cutting away.

## Decision

**In v0, rejected attestation does not silently mint ordinary authority. Ordinary issue/delivery lanes are fail-closed on `rejected`. Breakglass stays the explicit already-authoritative emergency lane that may still proceed while recording the rejected decision tuple.**

That means:

1. `workload-identity-issue-receipt` must never encode `attestation_verification.decision = rejected` because that receipt means an ordinary identity was actually issued.
2. `secret-receipt` ordinary delivery actions (`materialize`, `fetch`, `unseal`) must not succeed with `result = ok` when `attestation_verification.decision = rejected`.
3. If operators must proceed despite rejected posture, the action must move into an explicit emergency lane such as breakglass with its own receipt trail, not hide inside a successful ordinary issue/delivery receipt.
4. This cut does not define every future denial/event shape. It only forbids silent success in ordinary authority lanes.

## Consequences

### Positive

- Ordinary authority receipts remain semantically honest: successful issuance/delivery no longer carries a silent rejected-override story.
- Breakglass becomes more coherent as the one already-authoritative emergency lane instead of one emergency lane among many hidden ones.
- A/B/C/D can explain why ordinary authority failed closed and why recovery still happened using typed receipts rather than dashboards or ticket prose.

### Negative / limits

- This does **not** define a full denied-issuance receipt taxonomy for every lane.
- This does **not** settle the final product-profile sensitive-action set.
- Some future lanes may need explicit exception semantics; those should arrive later as explicit RFC/ADR work, not as implicit success on `rejected`.

## Why this is the right small hard decision now

This cut removes one more silent implementation choice without inventing a large new attestation exception subsystem.
It keeps the archive converging toward implementable truth:
**ordinary authority does not succeed on rejected posture unless the operator crossed an already-authoritative emergency lane.**
