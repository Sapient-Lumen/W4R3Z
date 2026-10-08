# trusted-publishing-tooling lane boundaries — 2026-03-21

This note keeps **P-0175 Trusted Publishing Tooling Kit** from collapsing into adjacent publish/security lanes.

## What this lane is for

This lane is for a **reviewable trusted-publishing rehearsal contract** over one release plan or CI run.
It should answer:

- which provider/host scope is in play,
- which claim basis defines trusted-publisher identity,
- whether the trigger is allowed,
- which publish mode the package/workspace expects,
- and what the rehearsal actually proved.

## Keep this distinct from nearby lanes

### Distinct from `P-0477 Cargo Publish Receipt Join Kit`

`P-0477` is the **post-publish** release-history receipt lane.
`P-0175` is the **pre-publish / rehearsal / claim-basis** lane.

### Distinct from `P-0492 Cargo Registry Auth Doctor Kit`

`P-0492` diagnoses auth/provider-stage failures across login/index/download/search/publish.
`P-0175` is specifically about trusted-publisher identity, trigger policy, and publish-mode rehearsal.

### Distinct from `P-0015 Cargo Attest`

`P-0015` is provenance/attestation publication.
`P-0175` is release-identity rehearsal before publish.

### Distinct from trust/risk lanes such as `P-0017 Trust Lens`

Trust/risk lanes reason about dependency risk and imported signals.
`P-0175` reasons about one crate’s publish identity and release path.

### Distinct from generic CI OIDC helper crates

Raw OIDC/JWT helper crates are substrate.
`P-0175` is the boring receiver-facing contract above provider-specific claims and crates.io trusted-publisher rules.

## Five truths this lane must keep separate

1. **provider scope** — GitHub Actions, GitLab.com, unsupported/self-hosted/manual-review provider, or future provider;
2. **claim basis** — issuer, audience, repository/project, workflow route, reusable-workflow route, ref, and environment identity;
3. **trigger policy** — eligible, blocked, unsupported, or manual-review-only;
4. **publish mode** — TP-only, mixed-mode migration, token fallback, or manual publish;
5. **rehearsal result** — observed pass, blocked, partial, inferred-only, or manual review;
6. **registry trust state** — what crates.io is actually configured to trust for the package set;
7. **workflow-route identity** — what direct/reusable/config route actually ran;
8. **authorization drift** — what changed between two release paths.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- GitLab.com support and self-hosted GitLab support,
- direct workflow identity and reusable-workflow route identity,
- repo-local publish policy and imported crates.io trust state,
- “OIDC exists” and “the claim basis needed by crates.io is visible and coherent”,
- allowed tag naming and an actually allowed trigger,
- trusted-publishing-only and mixed token fallback,
- a passing rehearsal and a completed publish,
- or pre-publish identity rehearsal and post-publish provenance.

## Preferred artifact vocabulary

- `provider-capability.matrix`
- `claim-basis.receipt`
- `release-trigger.report`
- `publish-mode.receipt`
- `publish-plan`
- `publish-rehearsal.report`
- `publish-session.receipt`
- `provider-drift.diff`
- `publish-support-bundle.manifest`
- `registry-publisher-state.import`
- `workflow-identity-route.receipt`
- `publish-authorization-drift.report`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.

Prefer importing registry state and route receipts explicitly rather than hiding them inside generalized claim-basis or rehearsal blobs.
