# Attestation-consuming action receipts pin the exact decision tuple

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

The archive already fixed the high-level attestation boundary:

- verifier outputs stay evidence-only,
- gate policy stays typed,
- and authoritative actions stay authoritative in their own receipts.

What still needed one more hard cut was the **action-side decision join**.
When an authoritative action receipt says attestation materially affected the decision, it should not leave the decisive tuple scattered across policy services, verifier databases, or operator memory.

Related:
- ADR: `adrs/ADR-0235-attestation-consuming-action-receipts-pin-the-exact-decision-tuple.md`
- evidence/admission boundary: `docs/492-attestation-results-evidence-and-admission-issue-boundary.md`
- posture receipts as evidence: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- profile default: `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`

## The boundary

For decisive consuming outcomes, `attestation_verification` must pin the full exact decision tuple and carry the exact pinned verdict mirror.

If `attestation_verification.decision` is one of:

- `accepted`
- `degraded`
- `rejected`

then the authoritative action receipt must also carry:

- `attestation_requirement_digest`
- `attestation_receipt_digest`
- `attestation_receipt_verdict`
- `attestation_admission_policy_digest`

This now applies to the canonical v0 consuming receipts:

- `secret-receipt`
- `breakglass-receipt`
- `workload-identity-issue-receipt`

## Why this was still missing

The archive had already narrowed the attestation lane substantially:

- routine reference authoring is cohort-shaped and replay-first,
- non-baseline references are explicit, timeboxed exceptions,
- renewals are digest-linked successor artifacts,
- reference selection is exact-digest-pinned,
- and attestation receipts that name an AK carry exact attester-provision provenance by digest.

But authoritative consuming receipts could still leave too much unsaid.
An action receipt could say “accepted” while forcing operators to reconstruct the rest from:

- a verifier database,
- a policy engine row,
- a server log,
- or a ticket note about which rule happened to be active.

That is too much hidden state for a product that is supposed to remain explainable across A/B/C/D.

## What the exact tuple answers

### 1) `attestation_requirement_digest`

This answers:
**what acceptance rule was applied?**

It keeps the freshness/minimum-verdict/runtime-evidence rule explicit.

### 2) `attestation_receipt_digest`

This answers:
**which exact verifier result was consumed?**

It keeps the consumed evidence result portable instead of making the authority story depend on an ephemeral verifier API response.

### 3) `attestation_receipt_verdict`

This answers:
**what exact verdict did the pinned verifier receipt actually contain?**

It keeps the source verdict visible at the same authority point instead of reinterpreting the same receipt later in service-side state.

### 4) `attestation_admission_policy_digest`

This answers:
**which gate policy/rule materially participated?**

It keeps “why was this action attestation-gated at all?” portable instead of pushing that answer into a policy database or control-plane memory.

## Why this matters for the product shapes

### A) Secure fleet host

A and D are the shapes most likely to gate secrets, maintenance, and identity issuance on measured posture.
They need consuming authority receipts that can be replayed and exported without relying on service-side state.

### B) Secure workstation

B cannot afford surprise ambient verifier dependence for ordinary local use.
But when sensitive operations are gated, the resulting action receipt should still explain the exact rule/result/policy tuple that participated.

### C) General-purpose OS

C keeps attestation optional.
That makes it even more important that optional gates stay explicit when they are used instead of becoming folklore about whichever verifier or broker happened to be deployed.

### D) Appliance factory / regulatory

Factories and regulated deployments often need the strongest portable proof for why a sensitive authority action happened.
Digest-bound joins are much easier to audit than policy-server archaeology.

## Guardrail

`tools/check_attestation_action_verification_contract.py`

This guardrail checks that:

- decisive `attestation_verification` outcomes require the full requirement/receipt/policy digest tuple in the canonical consuming authority schemas,
- the canonical examples exercise that exact tuple,
- and the attestation/admission/profile/runbook docs keep teaching the same no-hidden-policy-state boundary.

## Still open after this cut

This does not settle:

- which additional authority receipts beyond the v0 canonical three should adopt the same contract,
- the final user/operator UX for non-decisive states like `not-used`,
- or the full degraded/waived vocabulary for every attestation-consuming subsystem.

Those remain real implementation questions. A later archive cut narrows one of them already: there is no hidden degraded-waiver lane in v0, so `attestation_verification.decision = degraded` only makes sense when the consumed `attestation.requirement` itself already allows `attestation.requirement.min_verdict = degraded`.
A second narrow cut now narrows `rejected` too: successful ordinary issue/delivery lanes do not carry `rejected`. Ordinary secret delivery fails closed, workload identity issuance never silently mints an ordinary credential on `rejected`, and explicit emergency crossing belongs in breakglass instead.
But they no longer justify leaving decisive consuming attestation joins implicit, nor reinterpreting the exact pinned verdict after the fact.

Last updated: 2026-03-21r378
