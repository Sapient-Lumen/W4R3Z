# Trusted Publishing Tooling Kit — product plan (2026-03-21)

This note sharpens **P-0175 Trusted Publishing Tooling Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0175** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to become a universal publisher, a provenance platform, or a registry-auth debugger.
It should provide one boring, reviewable **trusted-publishing rehearsal contract** above today’s crates.io settings, GitHub/GitLab OIDC claims, and CI workflow routing.

`0.1` should make five things first-class:

1. **provider scope** — whether the plan depends on GitHub Actions, GitLab.com, or a host/provider that remains manual-review-only;
2. **claim basis** — which issuer, audience, repository/project, workflow route, reusable-workflow route, ref, and environment facts define trusted-publisher identity;
3. **trigger policy** — whether the current event is eligible, blocked, unsupported, or manual-review-only;
4. **publish mode** — trusted-publishing-only, mixed-mode migration, token fallback, or manual publish;
5. **rehearsal result** — which parts were observed, inferred, blocked, or still require human review.

## What `0.1` should provide other people

- one compact `provider-capability.matrix.json`
- one compact `claim-basis.receipt.json`
- one compact `release-trigger.report.json`
- one compact `publish-mode.receipt.json`
- one compact `publish-plan.json`
- one compact `publish-rehearsal.report.json`
- one compact `publish-session.receipt.json`
- one compact `provider-drift.diff.json`
- one compact `publish-support-bundle.manifest.json`
- one compact `publish.summary.md`
- a portable redacted support bundle

## Commands worth shipping first

- `cargo trusted-publish doctor`
- `cargo trusted-publish inspect-claims`
- `cargo trusted-publish classify-trigger`
- `cargo trusted-publish classify-mode`
- `cargo trusted-publish rehearse`
- `cargo trusted-publish diff`
- `cargo trusted-publish bundle`
- `cargo trusted-publish inspect`

## What to import, not reinvent

- crates.io trusted-publisher configuration and trusted-publishing-only mode as imported facts
- GitHub OIDC claim semantics, including reusable-workflow claim routing when present
- GitLab ID-token semantics, including `aud` and configurable `sub` posture
- current CI environment context and workflow metadata where available
- post-publish receipts and provenance only as adjacent layers, not built-in replacements

## Suggested `0.1` doctor warnings

- `provider_host_scope_not_supported`
- `id_token_permission_missing`
- `reusable_workflow_route_not_captured`
- `blocked_trigger_for_trusted_publishing`
- `trusted_publishing_only_but_token_fallback_declared`
- `mixed_workspace_publish_mode_needs_manual_review`
- `claim_basis_missing_audience_or_subject`
- `rehearsal_passed_but_publish_mode_still_ambiguous`

## First proving-ground scenarios

1. **A GitHub tag-release workflow is eligible only when the trusted-publisher claim basis and `id-token: write` posture are intact.**
2. **A reusable GitHub workflow needs `job_workflow_ref`-style route visibility; the caller workflow filename alone is not enough.**
3. **A blocked GitHub trigger stays blocked even if local policy naming looks release-like.**
4. **GitLab.com support and self-hosted GitLab remain different provider-scope claims until crates.io expands support.**
5. **Trusted-publishing-only and mixed token fallback must remain distinct publish modes in multi-package workspaces.**

## What to leave for later

- actual publish execution for every CI platform
- support for arbitrary/self-hosted providers beyond reviewable manual-review receipts
- provenance generation and signing workflows
- full registry-auth diagnosis for index/login/download/search failures
- registry-side public dashboards or incident notification systems

## `0.1` artifact vocabulary to stabilize first

### 1. `provider-capability.matrix.json`
Should answer:
- which provider family/host scope is being claimed,
- whether it is supported, partial, blocked, or manual-review-only,
- and which trigger or host caveats matter.

### 2. `claim-basis.receipt.json`
Should answer:
- which issuer and audience are expected,
- which repository/project and ref are in play,
- which workflow route or reusable-workflow route matters,
- and which environment context is part of the identity story.

### 3. `release-trigger.report.json`
Should answer:
- which event fired,
- why it is eligible/blocked/manual-review,
- and whether the verdict came from provider policy, crates.io policy, or missing evidence.

### 4. `publish-mode.receipt.json`
Should answer:
- whether the package/workspace is TP-only, mixed-mode, token-fallback, or manual,
- whether any package in the set violates the declared policy,
- and whether the current run is attempting a mode that the policy forbids.

### 5. `publish-rehearsal.report.json`
Should answer:
- whether provider scope, claim basis, trigger policy, and publish mode were all coherent,
- which checks were observational versus inferred,
- and what remains manual-review-only.

### 6. `provider-drift.diff.json`
Should answer:
- whether provider/host scope changed,
- whether claim-basis route changed,
- whether trigger policy changed,
- whether publish mode changed,
- and whether comparison is still honest.

## Definition of success for `0.1`

A maintainer should be able to answer, from one bundle alone:

> Which CI/provider identity would crates.io trust for this release, is the current trigger allowed, is the crate in trusted-publishing-only or mixed mode, and what changed compared with the last good release path?

If `0.1` can answer that clearly without secrets, it is already valuable.

## 2026-03-22 artifact-completeness addendum

The first product-plan pass was right to make provider scope, claim basis, trigger policy, publish mode, and rehearsal result first-class.
The sharper next move is to keep **three more truths** separate:

1. **imported registry state** — what crates.io is actually configured to trust;
2. **workflow-route identity** — what CI path actually ran, especially for reusable workflows or imported GitLab config;
3. **authorization drift** — what changed between two trusted-publish paths, even when both are green.

Near-term `0.1+` worth shipping:

- `cargo trusted-publish import-registry-state`
- `cargo trusted-publish inspect-route`
- `cargo trusted-publish diff-authz`

Plus three compact new artifacts:

- `registry-publisher-state.import.json`
- `workflow-identity-route.receipt.json`
- `publish-authorization-drift.report.json`

That keeps the lane bundle-first and reviewable without turning it into a generic JWT debugger or provenance system.

