# Trusted Publishing Tooling Kit — artifact-completeness plan (2026-03-22)

This note sharpens **P-0175 Trusted Publishing Tooling Kit** beyond its first product-plan pass.
The missing layer is no longer “can we rehearse OIDC publishing?”
It is “what exact registry state, workflow route, and authorization drift should another maintainer receive as a durable review object?”

## Main judgment

The next implementation pass should make three review objects first-class **above** the existing provider / claim / trigger / mode / rehearsal vocabulary:

1. **`registry-publisher-state.import.json`**
2. **`workflow-identity-route.receipt.json`**
3. **`publish-authorization-drift.report.json`**

Those objects do not replace existing receipts.
They stop future implementations from flattening registry state, CI route identity, and run-to-run authorization changes into one vague “trusted publishing is configured” story.

## What these artifacts should answer

### 1. `registry-publisher-state.import.json`
Should answer:
- which registry and package set were inspected;
- whether trusted-publishing-only is enabled;
- which trusted-publisher tuple is currently registered (provider, host scope, repository/project, workflow, environment);
- what source provided the observation (`crates_io_ui`, `iac_repo`, `manual_import`, or other imported route);
- and whether the imported state is authoritative, stale, partial, or manual-review-only.

This object exists because repo-local `publisher-policy.toml` and the registry’s actual state are useful but not identical truths.

### 2. `workflow-identity-route.receipt.json`
Should answer:
- which provider family emitted the identity;
- whether the route was direct, reusable, delegated, or still ambiguous;
- whether `id-token: write` / `id_tokens` posture was explicit;
- what caller workflow / config file and called workflow / route claims were observed;
- what environment / ref / ref-path / config-path claims materially shaped the route;
- and whether the receipt is observation, import, or manual reconstruction.

This object exists because claim-basis receipts often summarize identity facts, but downstream reviewers still need one compact answer to “what route actually ran?”

### 3. `publish-authorization-drift.report.json`
Should answer:
- what changed between two release paths;
- whether the change lives in registry state, provider host scope, workflow route, issuer, audience, trigger class, environment guard, or TP-only posture;
- whether the new path is compatible, blocked, degraded-to-manual-review, or ambiguous;
- and which old receipts remained comparable.

This object exists because release teams often need to know whether a moved workflow, changed environment, or provider migration meaningfully changed authorization posture even when both runs looked “green”.

## Receiver-facing contract

A worthy crate in this lane should give other people:

1. one imported registry-state receipt,
2. one workflow-route receipt,
3. one claim-basis receipt,
4. one trigger verdict,
5. one publish-mode receipt,
6. one rehearsal report,
7. one authorization-drift report,
8. and one portable redacted support bundle.

That package is more useful than another CI helper because it gives a maintainer a durable review surface instead of asking them to trust screenshots, YAML snippets, or half-redacted logs.

## First scenario families to prove

1. **Registry TP-only posture exists remotely even when the repo still carries mixed-mode planning language.**
2. **A reusable GitHub workflow needs an explicit route receipt; caller filename alone is not enough.**
3. **A GitLab route change in `ci_config_ref_uri`, `aud`, or environment guard should produce authorization drift even if the pipeline still minted a token.**
4. **A direct-workflow-to-reusable-workflow migration can be green but still needs route-drift review.**
5. **A support bundle must keep imported registry state, route receipts, and rehearsal observations separate.**

## Guardrails

Do not let future passes equate:

- repo-local policy with imported registry state,
- a decoded token with an honest route receipt,
- `id-token: write` with full release-route authorization,
- a passing rehearsal with a stable authorization contract,
- or GitLab.com support with arbitrary GitLab host support.

## Near-term implementation sketch

- keep the CLI bundle-first;
- add a `doctor --import-registry-state` mode that records imported crates.io trust state;
- add a `route` or `inspect-route` command that emits the workflow-route receipt;
- add a `diff-authz` command or report mode that compares two bundles and emits authorization drift;
- keep token material redacted by default and export only normalized claims/route facts.
