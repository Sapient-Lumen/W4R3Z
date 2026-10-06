# Attestation results evidence and admission-issue boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD already had evidence, requirement, and policy objects for remote attestation.
What it lacked was one crisp answer to another expensive question:

> Which object says “the verifier liked the evidence”, and which object actually says “issue the secret / credential / recovery session”?

This doc fixes that boundary for v0.

## Accepted boundary

DeriveBSD keeps **verifier results** and **issued authority** separate.

The verifier-evidence lane is:

- `boot.attestation`
- `attestation.reference`
- `attestation.requirement`
- `attestation.receipt`
- `attestation.admission.policy`

The action-authority lane stays action-specific:

- `secret-receipt`
- `breakglass-receipt`
- `workload-identity-issue-receipt`

That means:

- a passing `attestation.receipt` is not a secret grant
- a passing `attestation.receipt` is not a breakglass session approval
- a passing `attestation.receipt` is not a workload-identity issuance decision
- the action receipt remains the authoritative answer

## `attestation.receipt` stays evidence-only

`spec/attestation.receipt.schema.json` now carries `authority_semantics = attestation-evidence-only`.
That object records:

- which evidence was appraised
- which `attestation.reference` was used
- the verifier verdict and reasons
- an expiry / freshness window
- optional obligations or correlation pointers

This is reusable verifier evidence.
It is not the final authorization for a secret materialization, breakglass session, or credential issuance.

## `attestation.admission.policy` stays the gate map

`spec/attestation.admission.policy.schema.json` remains the place where DeriveBSD records:

- which action is attestation-gated
- which selector the rule applies to
- which `attestation.requirement` digest must be satisfied

This keeps “what is gated?” reviewable.
It also prevents raw verifier receipts from becoming accidental policy objects.

## `attestation.requirement` stays the acceptance rule

`spec/attestation.requirement.schema.json` is still the compact gate input that says:

- which `attestation.reference` digest applies
- optional verifier/policy digest bindings
- minimum acceptable verdict
- maximum receipt age
- whether runtime-integrity evidence is required

Subsystems should prefer requirement digests when expressing policy.
A raw receipt digest is only appropriate when a narrow workflow truly intends to pin one concrete verifier result.

## Action receipts carry `attestation_verification`

The action that **issues authority** should summarize the attestation decision it consumed.

In v0 the canonical surfaces are:

- `secret-receipt`
- `breakglass-receipt`
- `workload-identity-issue-receipt`

Those receipts may carry one `attestation_verification` object with:

- `decision`
- `attestation_requirement_digest`
- `attestation_receipt_digest`
- `attestation_admission_policy_digest`
- `notes`

For decisive consuming outcomes (`accepted`, `degraded`, `rejected`), that full exact decision tuple is now required, and the consuming receipt must also carry `attestation_receipt_verdict` so `accepted`→`pass`, `degraded`→`degraded`, and `rejected`→`fail` stay mirror-shaped. Authoritative action receipts may not reinterpret the exact pinned verifier outcome in service-side state. Degraded admission stays requirement-shaped too: if an action records `degraded`, the consumed `attestation.requirement` must already allow that posture (`min_verdict = degraded`), and v0 has no hidden degraded-waiver lane. Ordinary authority stays fail-closed on rejected posture as well: successful secret delivery or workload identity issuance cannot quietly carry `rejected`. Breakglass or a reviewed requirement/policy change stay the explicit alternatives when operators must proceed despite a stricter rule.

This is where the archive should answer:

- which requirement was applied
- which verifier result was accepted or rejected
- which attestation-admission policy materially gated the action
- whether the action proceeded under accepted / degraded / rejected posture
- and whether rejected posture stayed fail-closed in the ordinary lane or moved into an explicit emergency lane like breakglass
- and whether any post-breakglass ordinary resumption consumed a fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at` rather than reusing older evidence
- and whether that portable breakglass → attestation → ordinary-authority story stayed causally ordered instead of being reconstructed from backend state later

## Why this is the right narrow decision

This does not redesign remote attestation.
It only fixes the missing join so the archive stops blurring:

- verifier evidence,
- gate policy,
- and issued authority.

That is a small, high-leverage change because it makes future implementation choices cheaper and more explainable.

## Product-shape fit (A–D without forks)

- **A / fleet host:** sensitive secret release, rollout, and recovery lanes can require fresh attestation without letting verifier reachability become silent standing authority; breakglass is not standing ordinary authority either. For post-breakglass ordinary resumption, the pinned `attestation.receipt.created_at` must be strictly later than the relevant breakglass receipt `created_at`, and the later ordinary receipt must not predate the pinned `attestation.receipt.created_at`.
- **B / workstation:** attestation can still gate sensitive operations, but the host can explain the exact consuming decision instead of presenting a raw verifier verdict as ambient truth.
- **C / general-purpose OS:** optional attestation lanes remain optional because action receipts, not raw verifier results, say whether anything was actually gated.
- **D / appliance factory / regulatory:** production enrollment and maintenance lanes gain durable, replayable action receipts tied to explicit verifier evidence and requirement policy.

## Related docs

- `adrs/ADR-0082-attestation-results-evidence-and-admission-issue-boundary.md`
- `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- `docs/388-remote-attestation-admission-and-enrollment.md`
- `docs/181-workload-identity-and-secretless-deploys.md`
- `docs/223-secrets-and-key-management-as-evidence.md`
- `docs/236-breakglass-and-recovery-mode.md`
- `docs/440-attestation-admission-policy-diff-as-review-surface.md`
- `spec/attestation.receipt.schema.json`
- `spec/attestation.requirement.schema.json`
- `spec/attestation.admission.policy.schema.json`
- `spec/secret.receipt.schema.json`
- `spec/breakglass.receipt.schema.json`
- `spec/workload.identity.issue.receipt.schema.json`

That post-breakglass resumption check is exact-joined and same-host bound now too: when breakglass materially gated an ordinary authority decision, the consuming receipt carries `relevant_breakglass_receipt_digest` so the exact breakglass receipt can be reviewed alongside the pinned attestation receipt instead of inferred later. The two joined receipts must still refer to the same host rather than normalizing cross-host join folklore, and the portable causal story should not depend on backend row order to infer freshness.
Last updated: 2026-03-21r382
