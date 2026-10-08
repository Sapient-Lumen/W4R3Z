# Frontier salience note — 2026-03-22 (192)

## Main judgment

The archive should spend another pass on **P-0175 Trusted Publishing Tooling Kit** before widening into another adjacent supply-chain, provenance, or CI-auth sector.

## Why

Current crates.io, RFC, GitHub, GitLab, and Rust Infrastructure sources make the missing layer sharper than “better OIDC publishing tooling”:

- RFC 3691 still defines trusted publishing as a short-lived token exchange model rather than a long-lived secret model.
- crates.io now supports GitHub Actions and GitLab CI/CD trusted publishing, but current GitLab support still stops at **GitLab.com**.
- crates.io now exposes **Trusted Publishing Only Mode** and explicitly blocks `pull_request_target` and `workflow_run` GitHub triggers.
- GitHub OIDC docs keep reusable-workflow route identity and `job_workflow_ref` materially distinct from the caller workflow’s default claims.
- GitLab ID-token docs keep host/issuer scope, `aud`, configurable `sub`, and `ci_config_ref_uri` materially meaningful.
- Rust Infrastructure is now managing trusted-publishing configuration as IaC, which makes imported registry policy versus repo-local route policy a real comparison problem.

The missing crate is therefore not another JWT decoder, another YAML template pack, or another provenance layer.
It is a receiver-facing contract for:

1. **imported registry trust state**,
2. **workflow-route identity**,
3. **claim-basis / trigger / publish-mode coherence**,
4. **authorization drift across releases**, and
5. **portable redacted support bundles**.

## Ranking consequence

Raise **P-0175** back into the lead cluster for the next few passes.
The lane is most worthy when it keeps registry imports, workflow-route receipts, claim-basis receipts, and authorization-drift reports distinct from broader auth/provenance/publish-history lanes.

## What not to do

Do not spend the next pass on:

- another generic OIDC claim inspector,
- another reusable-workflow helper without bundle exports,
- another supply-chain dashboard,
- or another provenance/attestation wrapper.

Those are adjacent at best.
The sharper missing value is the boring contract another maintainer can review and diff.
