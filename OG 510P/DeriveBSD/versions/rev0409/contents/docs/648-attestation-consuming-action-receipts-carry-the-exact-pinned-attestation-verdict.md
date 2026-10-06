# Attestation-consuming action receipts carry the exact pinned attestation verdict

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt

The archive already fixed several major attestation questions:

- consuming receipts pin the exact requirement/receipt/policy tuple,
- degraded admission must already be present in the consumed requirement,
- and ordinary secret/identity lanes stay fail-closed on rejected posture.

What still needed one more narrow cut was semantic drift **inside the consuming receipt itself**.
A receipt could pin the exact `attestation.receipt` digest, but still summarize a slightly different verdict story.
That would make verifier dashboards, service rows, or operator memory the real place you have to go to answer the simple question:
**what exact verdict did the pinned attestation receipt actually contain?**

Related:
- ADR: `adrs/ADR-0238-attestation-consuming-action-receipts-carry-the-exact-pinned-attestation-verdict.md`
- exact decision tuple boundary: `docs/645-attestation-consuming-action-receipts-pin-the-exact-decision-tuple.md`
- degraded-admission boundary: `docs/646-attestation-degraded-admission-stays-requirement-shaped-and-no-hidden-waivers.md`
- rejected ordinary-authority boundary: `docs/647-rejected-attestation-does-not-silently-mint-ordinary-authority-breakglass-stays-explicit.md`

## The boundary

For decisive consuming outcomes, `attestation_verification` now also carries `attestation_receipt_verdict`.

That field is the **exact verdict** from the pinned `attestation.receipt`:

- `pass`
- `degraded`
- `fail`

The consuming receipt still keeps its compact authority-side summary, but that summary is now a fixed projection rather than a reinterpretation:

- `accepted` → `pass`
- `degraded` → `degraded`
- `rejected` → `fail`

In plain terms:

- action receipts may summarize the gate they consumed,
- but they may not rewrite the exact verdict already carried by the pinned verifier receipt.

## Why this matters

### 1) It removes another hidden backend-state seam

If the consuming receipt only names the pinned attestation digest but not the exact verdict it mirrored, operators still need verifier-specific state to prove whether the source verdict was `pass`, `degraded`, or `fail`.
That pushes semantic truth back into dashboards and service rows.

### 2) It keeps compact authority summaries useful without letting them become folklore

`accepted`, `degraded`, and `rejected` are good action-side vocabulary.
They explain what the consuming authority actually did.
But they are not a license to reinterpret the underlying attestation receipt.
The mirror field keeps the original verifier vocabulary visible at the consumption point.

### 3) It keeps A/B/C/D portable

- **A / fleet host:** secret brokers and identity issuers can export one exact tuple plus one exact mirrored verdict without backend archaeology.
- **B / workstation:** trusted UI can explain both the consumed verifier verdict and the action-side consequence directly from the receipt trail.
- **C / general-purpose OS:** optional attestation remains explicit when present instead of turning into “some service said accepted.”
- **D / appliance factory / regulatory:** audit review can prove the precise source verdict in the same authority receipt that justified or denied the action.

## Schema/example consequence

The canonical consuming receipts now teach this explicitly:

- `spec/secret.receipt.schema.json`
- `spec/breakglass.receipt.schema.json`
- `spec/workload.identity.issue.receipt.schema.json`

For decisive outcomes they now require:

- `attestation_requirement_digest`
- `attestation_receipt_digest`
- `attestation_receipt_verdict`
- `attestation_admission_policy_digest`

And they enforce the fixed projection mapping:

- `accepted` pairs with `attestation_receipt_verdict = pass`
- `degraded` pairs with `attestation_receipt_verdict = degraded`
- `rejected` pairs with `attestation_receipt_verdict = fail`

The canonical examples now carry that field too:

- `spec/examples/secret.receipt.json`
- `spec/examples/secret.receipt.degraded.json`
- `spec/examples/secret.receipt.rejected.json`
- `spec/examples/breakglass.receipt.json`
- `spec/examples/breakglass.receipt.rejected.json`
- `spec/examples/workload.identity.issue.receipt.json`

## Guardrail

`tools/check_attestation_verdict_projection_contract.py`

This guardrail checks that:

- decisive consuming receipts require `attestation_receipt_verdict`,
- the schemas teach the fixed mirror mapping (`accepted`→`pass`, `degraded`→`degraded`, `rejected`→`fail`),
- and the canonical examples keep the exact pinned-verdict mirror explicit instead of relying on service-side reinterpretation.

## What stays open

This cut does **not** settle:

- every future action receipt that might eventually adopt `attestation_verification`,
- the full denied-event vocabulary around attestation consequences,
- or whether richer verifier reasoning should later be projected into separate evidence exports.

One later archive cut now narrows the next adjacent seam too: after breakglass, ordinary authority only resumes on fresh post-breakglass attestation rather than by reusing older accepted/degraded evidence.

It only makes one narrow decision now:
**a consuming receipt may summarize the action-side consequence, but it may not reinterpret the exact verdict in the pinned attestation receipt.**

Last updated: 2026-03-21r379
