# Supplychain verification evidence and publish-gate boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, supply-chain, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already had the pieces for workflow verification:

- DSSE / in-toto attestations,
- optional `supplychain-layout-policy`,
- optional `supplychain-verify-receipt`,
- and the release-authority lane.

What it lacked was one crisp answer to a costly question:

> Which object says “the workflow evidence checked out”, and which object actually says “ship this release”?

This doc fixes that boundary for v0.

## Accepted boundary

DeriveBSD keeps **workflow verification** and **publication authority** separate.

The workflow-verification lane is:

- `supplychain-layout-policy`
- `supplychain-verify-receipt`
- DSSE / in-toto statements and other consumed evidence

The publication-authority lane is still:

- `release.authority.policy`
- `release.publish.receipt`

That means:

- a provenance statement is not a publish approval
- a passing workflow-verification receipt is not a publish approval
- a VSA-like verifier summary is not a publish approval
- `release.publish.receipt` is still the authoritative answer

## `supplychain-layout-policy` is a workflow-constraint policy

`spec/supplychain.layout.policy.schema.json` stays the place where DeriveBSD records:

- which layout digest applies,
- which trust roots / authorities define the workflow,
- which predicate types or adjunct evidence are required,
- and whether verification failures are advisory or denying.

It is a policy object, but not the publication-authority policy.
Its job is to constrain workflow verification, not to authorize shipping by itself.

## `supplychain-verify-receipt` is workflow-verification evidence only

The schema now carries `authority_semantics = workflow-verification-evidence-only`.
A receipt should bind:

- `layout_policy_digest`
- `artifact_digest`
- the digests of consumed evidence
- the verifier result (`pass` or `fail`)
- optional context such as the plan / policy decision

A `pass` means the verifier concluded that the subject satisfied the named workflow policy.
It does **not** mean the subject is automatically authorized for release.

## Release authority may require workflow verification, but does not outsource authority

`release.authority.policy` may include `supplychain_verification` rules such as:

- mode (`ignored`, `optional`, `required`)
- `allowed_layout_policy_digests`
- `require_pass_result`
- freshness limits via `max_receipt_age`

Those rules only decide what workflow-verification evidence must be present before publication may proceed.
They do **not** move authority into CI, a layout file, or a verifier backend.

## `release.publish.receipt` is the gate summary join point

Publish receipts should not grow ad-hoc top-level workflow-verification fields.
Instead they may carry one `supplychain_verification` summary object.

That summary should record:

- decision (`not-required`, `not-used`, `accepted`, `rejected`)
- `verify_receipt_digests`
- optional `layout_policy_digests`
- notes

This is the only place where workflow-verification evidence becomes a publish-time gate result.

## Attestations remain inputs, not silent authority

The archive already emits or contemplates evidence such as:

- provenance statements,
- SBOM statements,
- VEX statements,
- test receipts,
- in-toto links,
- and optional VSA-like summaries.

Those are valuable, but they should remain **inputs** to verifiers and policy engines.
Treating them as automatic release authority would collapse too many lanes:

- workflow evidence,
- verifier judgment,
- and final publication approval.

## Product-shape fit (A–D without forks)

- **A / fleet host:** workflow verification can be mandatory and mirrored, while final publication still stays threshold-bound and explainable offline.
- **B / workstation:** provenance and CI quality remain visible and useful without turning remote verifier stacks into hidden trust anchors.
- **C / general-purpose OS:** local/admin workflows can keep optional verification and compatibility adapters without pretending every build is a release pipeline.
- **D / appliance factory / regulatory:** audited workflow verification can be retained as evidence while the actual publish / import / promote authority remains explicit and offline-capable.

## Why this is the right narrow decision

This does not redesign the build pipeline.
It only fixes the join boundary so the archive stops blurring:

- statements,
- verifier outputs,
- and publication authority.

That is small, practical, and worth implementing later because it makes the future release path cheaper to reason about.

## Related docs

- `adrs/ADR-0079-supplychain-verification-evidence-and-publish-gate-boundary.md`
- `docs/202-in-toto-layouts-and-step-policy.md`
- `docs/71-attestations-dsse-in-toto-slsa.md`
- `docs/31-provenance-and-sbom.md`
- `docs/260-release-authority-policy-and-key-management.md`
- `docs/229-evidence-spine-overview.md`
- `spec/supplychain.layout.policy.schema.json`
- `spec/supplychain.verify.receipt.schema.json`
- `spec/release.authority.policy.schema.json`
- `spec/release.publish.receipt.schema.json`

Last updated: 2026-03-07r218
