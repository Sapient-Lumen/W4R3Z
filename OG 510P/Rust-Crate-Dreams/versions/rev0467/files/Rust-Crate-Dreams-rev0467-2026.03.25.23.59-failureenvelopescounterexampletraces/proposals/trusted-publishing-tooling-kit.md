---
id: P-0175
title: Trusted Publishing Tooling Kit — provider-scope matrices, claim-basis receipts, trigger-policy reports, and publish-mode gates
status: idea
domains: [cargo, publishing, registries, ci, supply-chain, security, release-engineering, github-actions, gitlab]
last_reviewed: 2026-03-22
evidence:
  - https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://crates.io/docs/trusted-publishing
  - https://docs.github.com/en/actions/reference/security/oidc
  - https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-cloud-providers
  - https://docs.github.com/actions/deployment/security-hardening-your-deployments/using-openid-connect-with-reusable-workflows
  - https://docs.gitlab.com/ci/secrets/id_token_authentication/
  - https://docs.gitlab.com/ci/yaml/
  - https://blog.rust-lang.org/inside-rust/2026/01/13/infrastructure-team-q4-2025-recap-and-q1-2026-plan/
---

# P-0175 — Trusted Publishing Tooling Kit

**Codename:** `trustedpublish`

**Primary surface:** a crate workspace plus `cargo trusted-publish`.

**Canonical artifact:** `*.publishbundle.zip`.

## Problem

crates.io trusted publishing is now real enough that the missing value is no longer “OIDC exists somewhere on the roadmap”.
The ecosystem has crossed into a more interesting phase:

- RFC 3691 gives crates.io an explicit OIDC-based publish identity model with short-lived access tokens and restricted workflow claims;
- crates.io now supports **GitHub Actions** and **GitLab CI/CD** trusted publishing, but GitLab support is currently limited to **GitLab.com** rather than arbitrary self-hosted instances;
- crate owners can now enable **trusted-publishing-only mode**, disabling traditional API-token publishes for that crate;
- crates.io now blocks especially risky GitHub Actions triggers such as `pull_request_target` and `workflow_run` from trusted publishing;
- GitHub’s OIDC model exposes reusable-workflow routing facts like `job_workflow_ref` and requires explicit `id-token: write` permission to mint an OIDC token;
- GitLab ID tokens expose a configurable `aud` claim and a `sub` claim that can incorporate project/ref/environment context, which means claim shape is provider-specific rather than generic “CI identity”.

That is enough substrate that maintainers now need a boring answer to questions like:

- does this repository/workflow/environment/trigger combination actually satisfy crates.io trusted-publisher expectations,
- which **provider/host scope** is in play and whether that host is supported at all,
- which exact **identity claims** or route facts another reviewer should inspect,
- whether **trusted-publishing-only mode** will block a mixed token+OIDC release plan,
- what changed when a team moved from a direct workflow to a reusable workflow or from GitHub to GitLab,
- and what compact artifact should another maintainer review instead of scanning CI YAML, screenshots, and half-redacted logs?

The missing crate is **not** crates.io trusted publishing itself.
It is **not** a provenance attestation system, a registry-auth doctor, or a post-publish receipt join.
The missing crate is a **Trusted Publishing Tooling Kit**: one receiver-facing contract for trusted-publisher rehearsal above crates.io settings, provider OIDC claims, CI workflow routing, and publish-mode policy.

## Main judgment

A worthy crate here should help other people review five separate truths before they trust a release path:

1. **provider scope** — GitHub Actions, GitLab.com, a not-yet-supported/self-hosted provider, or manual-review-only;
2. **claim basis** — which repository, workflow, reusable-workflow route, environment, issuer, subject, and audience facts actually define release identity;
3. **trigger policy** — whether the current event is eligible, blocked, unsupported, or only manually reviewable;
4. **publish mode** — trusted-publishing-only, mixed token+OIDC migration, manual publish, or workspace-split mode;
5. **rehearsal result** — what was actually validated, what remained inferred, and what still requires human review.
6. **registry/import honesty** — what crates.io is actually configured to trust versus what the repository merely declares.
7. **workflow-route honesty** — what release path actually ran, especially when reusable workflows or imported CI config are involved.
8. **authorization-drift honesty** — what changed between two trusted-publish paths, even when both appear green.

## What it provides

- `provider-capability.matrix.json` — records supported provider families, host/issuer scope, trigger-policy notes, and manual-review boundaries.
- `claim-basis.receipt.json` — normalized trusted-publisher identity facts for one plan or run: provider, issuer, audience, repository/project, workflow route, reusable workflow route when applicable, ref context, and environment context.
- `release-trigger.report.json` — explains whether the current event is eligible, blocked, unsupported, or manual-review-only and why.
- `publish-mode.receipt.json` — records whether the package/workspace expects trusted-publishing-only, mixed-mode migration, token fallback, or manual publish.
- `publish-plan.json` — normalized release plan for packages, versions, provider, trigger, workflow, environment, and rehearsal/publish mode.
- `publish-rehearsal.report.json` — records one non-publishing rehearsal with provider verdict, claim-basis verdict, trigger verdict, publish-mode verdict, and missing prerequisites.
- `publish-session.receipt.json` — records one actual or rehearsed publish attempt with provider, workflow route identity, claimed mode, and high-level outcome.
- `provider-drift.diff.json` — compares two runs and classifies `provider_scope_changed`, `claim_basis_changed`, `trigger_policy_changed`, `publish_mode_changed`, `issuer_scope_changed`, `audience_claim_changed`, and `manual_review_required`.
- `registry-publisher-state.import.json` — imported crates.io-side trusted-publisher configuration for the package set.
- `workflow-identity-route.receipt.json` — direct/reusable/config-route receipt for what path actually ran.
- `publish-authorization-drift.report.json` — release-to-release authorization drift for registry state, route, issuer/audience, trigger, environment, and TP-only posture.
- `publish-support-bundle.manifest.json` — enumerates attached plans, receipts, reports, notes, and redaction posture for a `*.publishbundle.zip` support bundle.
- `cargo trusted-publish doctor` — checks policy, provider support, trigger eligibility, and publish-mode coherence.
- `cargo trusted-publish inspect-claims` — decodes and normalizes the current provider-specific claim basis without exporting raw tokens.
- `cargo trusted-publish rehearse` — validates the plan without publishing.
- `cargo trusted-publish diff` — compares two release/rehearsal bundles.
- `cargo trusted-publish bundle` — emits one redacted support artifact.

## What the crate should provide other people

1. **Provider-scope honesty** so GitHub Actions, GitLab.com, and future/self-hosted providers stop being blurred into one fake “OIDC publishing works here” claim.
2. **Claim-basis honesty** so repository identity, workflow route, reusable-workflow route, issuer, audience, and environment are visible and diffable.
3. **Trigger-policy honesty** so blocked GitHub triggers and provider-specific event rules do not masquerade as acceptable release paths.
4. **Publish-mode honesty** so trusted-publishing-only, mixed-mode migration, and manual/token fallback are treated as distinct operational states.
5. **One boring support bundle** that release engineers, maintainers, and security reviewers can inspect without rerunning CI or asking for full secrets-laden logs.
6. **Registry-state honesty** so repo policy and crates.io policy stop being conflated.
7. **Workflow-route honesty** so direct workflows, reusable workflows, and imported CI config routes are visible and diffable.
8. **Authorization-drift honesty** so “still green” is not mistaken for “same release authorization story”.

## Persona / who it’s for

- maintainers moving from token-based CI publishing to trusted publishing
- organizations enforcing trusted-publishing-only mode
- release engineers running multi-crate workspaces
- platform/security teams reviewing CI release posture
- incident responders reconstructing why a trusted publish was or was not allowed

## Users & user stories

- **Maintainer**: “Tell me whether our GitHub or GitLab release workflow is actually eligible for trusted publishing before I tag a release.”
- **Release engineer**: “Show me which repository/workflow/environment claims crates.io is really depending on, especially if we use reusable workflows.”
- **Security reviewer**: “Show whether this crate is trusted-publishing-only or still has token fallback, and whether the current trigger was blocked or only conditionally eligible.”
- **Platform team**: “Diff two repositories and tell me whether the trusted-publisher route changed because the provider, issuer scope, workflow route, or audience claims changed.”

## Prior art (and why it’s insufficient)

- crates.io trusted publishing already exists and is a major security improvement.
- RFC 3691 defines the OIDC model and its security posture.
- crates.io’s January 2026 development update added GitLab support, trusted-publishing-only mode, and blocked-trigger rules.
- GitHub and GitLab already document the OIDC / ID-token claims available from their CI systems.
- The archive already has **P-0477 Cargo Publish Receipt Join Kit**, which is about **post-publish release receipts**.
- The archive already has **P-0492 Cargo Registry Auth Doctor Kit**, which is about **client-side auth/provider-stage diagnosis**.
- The archive already has **P-0015 Cargo Attest**, which is about **artifact provenance attestations**.

What remains missing is one **preflight / rehearsal / claim-basis / publish-mode artifact** for trusted publishing itself.

## Design goals

1. **Rehearsal-first** — trusted publishing should be testable before a live release.
2. **Provider-scope explicit** — GitHub Actions, GitLab.com, and future/self-hosted providers must stay visibly distinct.
3. **Claim-basis explicit** — repository, workflow route, reusable-workflow route, issuer, audience, and environment context must be reviewable.
4. **Trigger-explicit** — workflow event policy must be first-class.
5. **Publish-mode explicit** — trusted-publishing-only, mixed-mode, and fallback/manual routes must stay visible.
6. **Redaction-first** — exported artifacts must explain identity and policy without leaking raw OIDC tokens.

## MVP surface

- Minimal types: `PublisherPolicy`, `ProviderCapabilityMatrix`, `ClaimBasisReceipt`, `ReleaseTriggerReport`, `PublishModeReceipt`, `PublishPlan`, `PublishRehearsalReport`, `PublishSessionReceipt`, `ProviderDriftDiff`, `RegistryPublisherStateImport`, `WorkflowIdentityRouteReceipt`, `PublishAuthorizationDriftReport`, `PublishSupportBundleManifest`
- Minimal functions:
  - `load_publisher_policy()`
  - `inspect_claim_basis()`
  - `classify_release_trigger()`
  - `classify_publish_mode()`
  - `rehearse_publish()`
  - `capture_publish_session_receipt()`
  - `diff_publish_sessions()`
  - `write_publish_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `github-actions`
  - `gitlab-ci`
  - `crates-io`
  - `markdown`

## Compatibility story

- Must work with crates.io-first trusted publishing.
- Must clearly distinguish **supported**, **blocked**, **unsupported**, and **manual-review** provider/trigger states.
- Should model GitHub Actions and GitLab.com first without pretending all CI systems have the same identity shape.
- Must keep **GitLab.com support** distinct from **self-hosted GitLab manual-review boundaries** until crates.io supports more than GitLab.com.
- Must remain useful for repositories still in mixed mode, where some crates use tokens and some use trusted-publishing-only mode.
- Should compose with post-publish receipts and provenance layers rather than replacing them.

## Conformance & fixtures

- A GitHub Actions tag-release fixture with valid direct-workflow claims and successful rehearsal.
- A GitHub reusable-workflow fixture where `job_workflow_ref` is the important route fact.
- A GitHub Actions blocked-trigger fixture for `pull_request_target` or `workflow_run`.
- A GitLab.com trusted-publisher fixture with trusted-publishing-only expectations.
- A GitLab self-managed/manual-review fixture that stays distinct from GitLab.com support.
- A mixed-workspace fixture where one package expects trusted publishing and another still requires token/manual review.

## Path to boring stability

- Freeze the claim-basis / publish-mode / rehearsal schema before adding provider-specific bells and whistles.
- Start with doctor + claim inspection + rehearsal + diff + bundle export; do not try to become a universal publisher on day one.
- Keep provider capability reporting coarse and reviewable.
- Treat unknown providers or incomplete claim semantics as `manual_review_required`, not implicit support.

## Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

## Minimum lovable MVP

A cargo subcommand that reads one repository’s trusted-publishing policy, normalizes the current provider-specific claim basis, classifies the current CI trigger/provider as eligible or blocked, rehearses the publish path without releasing, and emits one redacted bundle describing the decision.

## De-risk plan

1. Start with GitHub Actions and GitLab.com because crates.io explicitly supports those.
2. Treat actual publish execution as optional; rehearsal and claim inspection are the primary value.
3. Keep the first release focused on crates.io trusted publishing rather than abstract registry support.
4. Validate first on one tag-driven release workflow, one reusable-workflow case, one blocked-trigger case, and one GitLab.com case.

## Non-goals

- Not a replacement for crates.io’s trusted publishing implementation.
- Not a provenance attestation system.
- Not a post-publish checksum/history bundle.
- Not a general secret manager or registry-auth replacement.
- Not a universal CI OIDC abstraction for every provider on day one.

## Architecture & API sketch

```rust
pub enum TriggerVerdict {
    Eligible,
    Blocked,
    Unsupported,
    ManualReviewRequired,
}

pub fn inspect_claim_basis(env: &CiEnv) -> ClaimBasisReceipt;
pub fn classify_release_trigger(plan: &PublishPlan, env: &CiEnv) -> ReleaseTriggerReport;
pub fn classify_publish_mode(policy: &PublisherPolicy, packages: &[Package]) -> PublishModeReceipt;
pub fn import_registry_publisher_state(source: &RegistrySource) -> Result<RegistryPublisherStateImport>;
pub fn inspect_workflow_identity_route(env: &CiEnv) -> WorkflowIdentityRouteReceipt;
pub fn rehearse_publish(plan: &PublishPlan, policy: &PublisherPolicy) -> Result<PublishRehearsalReport>;
pub fn diff_publish_authorization(old: &PublishSupportBundleManifest, new: &PublishSupportBundleManifest) -> PublishAuthorizationDriftReport;
pub fn write_publish_bundle(bundle: &PublishSupportBundleManifest, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `publisher-policy.toml`, `registry-publisher-state.import.json`, `provider-capability.matrix.json`, `workflow-identity-route.receipt.json`, `claim-basis.receipt.json`, `publish-mode.receipt.json`, `publish-plan.json`, `release-trigger.report.json`, `publish-rehearsal.report.json`, `publish-session.receipt.json`, `provider-drift.diff.json`, `publish-authorization-drift.report.json`, `publish-support-bundle.manifest.json`, `notes.md`.

## Security / safety model

- Never persist raw OIDC or access tokens in exported bundles.
- Preserve enough repository/workflow/environment detail to support review and audits.
- Distinguish observed provider facts from inferred policy expectations.
- Distinguish provider support from host/issuer support.
- Prefer `manual_review_required` to silent success when provider semantics are incomplete.

## Maintenance & governance plan

- Track crates.io trusted publishing changes, provider additions, and trigger-policy changes.
- Keep provider capability vocabularies compact and versioned.
- Maintain fixtures for GitHub direct workflows, GitHub reusable workflows, GitHub blocked triggers, GitLab.com, self-hosted/manual-review boundaries, and trusted-publishing-only drift.
- Publish guidance on how these artifacts compose with post-publish receipts and attestations.

## Milestones

### 0.1
- policy format
- provider capability matrix
- claim-basis inspection
- trigger / publish-mode classification
- doctor + rehearsal reports

### 0.2
- session receipts
- provider drift diffs
- crates.io trusted-publishing-only checks
- reusable-workflow route support

### 1.0
- stable bundle schema
- curated provider/trigger fixture corpus
- CI templates and review guidance

## Open questions

- What is the smallest provider vocabulary that still distinguishes GitHub, GitLab.com, and future manual-review providers meaningfully?
- Which claim fields are stable enough to freeze across GitHub direct workflows, reusable workflows, and GitLab subject customization without overfitting?
- How much of the final crates.io trusted-publishing configuration can be observed directly versus declared locally?
- Which mixed-mode workspace cases deserve first-class support instead of `manual_review_required`?

## Sources

- RFC 3691 trusted publishing for crates.io: https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
- crates.io development update (2026-01-21): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io trusted publishing docs: https://crates.io/docs/trusted-publishing
- GitHub OIDC reference: https://docs.github.com/en/actions/reference/security/oidc
- GitHub OIDC permission guidance: https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-cloud-providers
- GitHub reusable workflow OIDC claims: https://docs.github.com/actions/deployment/security-hardening-your-deployments/using-openid-connect-with-reusable-workflows
- GitLab ID token auth docs: https://docs.gitlab.com/ci/secrets/id_token_authentication/
- GitLab CI YAML `id_tokens` docs: https://docs.gitlab.com/ci/yaml/
