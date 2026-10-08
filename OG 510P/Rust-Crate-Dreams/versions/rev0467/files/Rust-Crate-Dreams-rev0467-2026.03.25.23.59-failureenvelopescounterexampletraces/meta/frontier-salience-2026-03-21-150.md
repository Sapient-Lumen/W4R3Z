# Frontier salience snapshot — 2026-03-21-150

This pass did **not** add another provenance bundle, another registry-auth doctor, or another generic CI OIDC helper.
It deepened **P-0175 Trusted Publishing Tooling Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- crates.io trusted publishing now supports **GitHub Actions** and **GitLab CI/CD**, but GitLab support is currently **GitLab.com-only**;
- crates can now enable **trusted-publishing-only mode**, which turns migration/fallback posture into a first-class review concern;
- crates.io now blocks risky GitHub Actions triggers such as `pull_request_target` and `workflow_run` from trusted publishing;
- GitHub’s OIDC model exposes route facts such as `job_workflow_ref` for reusable workflows and requires explicit `id-token: write` permission;
- GitLab ID tokens expose a configurable `aud` plus a `sub` claim that can now incorporate more ref/environment context.

That combination means “supports trusted publishing” is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. provider-scope truth,
2. claim-basis truth,
3. trigger-policy truth,
4. publish-mode truth,
5. and rehearsal-result truth.

## Main conclusion

Promote **P-0175** again, but keep it narrow.
The sharper next move is not a universal publisher.
It is a boring contract that keeps **provider/host support**, **claim route**, **trigger eligibility**, and **TP-only versus mixed-mode release posture** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0175 Trusted Publishing Tooling Kit** — strengthened because the ecosystem now has real provider diversity, TP-only mode, blocked-trigger policy, and provider-specific claim routes.
2. **P-0477 Cargo Publish Receipt Join Kit** — still strong because post-publish confirmation remains a distinct lane from preflight identity rehearsal.
3. **P-0492 Cargo Registry Auth Doctor Kit** — still strong because publish identity does not solve broader registry auth-stage diagnosis.
4. **P-0017 Trust Lens** — still strong because publish identity is one trust input, not the whole dependency-risk story.
5. **P-0035 cargo-build-insights** — still strong because build-history evidence remains one of the most practical cross-cutting workbench seams.

## Keep these boundaries sharp

- **P-0175** is provider-scope + claim-basis + trigger-policy + publish-mode + rehearsal-result truth.
- post-publish release receipts are separate.
- provenance/attestation is separate.
- registry-auth diagnosis is separate.
- public incident communication is separate.

Do not let “trusted publishing” flatten those into one fake crate.
