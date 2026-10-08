# Trusted Publishing Tooling Kit fixtures

These fixtures exercise the `0.1` artifact vocabulary for **P-0175 Trusted Publishing Tooling Kit**.

## Core schemas

- `provider-capability.matrix.schema.json`
- `claim-basis.receipt.schema.json`
- `release-trigger.report.schema.json`
- `publish-mode.receipt.schema.json`
- `publish-plan.schema.json`
- `publish-rehearsal.report.schema.json`
- `publish-session.receipt.schema.json`
- `provider-drift.diff.schema.json`
- `publish-support-bundle.manifest.schema.json`
- `registry-publisher-state.import.schema.json`
- `workflow-identity-route.receipt.schema.json`
- `publish-authorization-drift.report.schema.json`

## Scenario families

- `github_actions_tag_release/` — a direct GitHub workflow with explicit claim basis, TP-only/mode posture, and successful rehearsal.
- `github_actions_blocked_trigger/` — a blocked GitHub trigger must stay blocked even when local release naming looks plausible.
- `github_reusable_workflow_route_requires_job_workflow_ref/` — reusable workflow route identity is not the same as the caller workflow filename.
- `gitlab_tp_only_release/` — GitLab.com TP-only flows need explicit audience/subject and mode posture.
- `gitlab_self_managed_host_scope_requires_manual_review/` — GitLab.com support must stay distinct from self-managed GitLab host scope.
- `mixed_workspace_token_fallback_is_not_tp_only_green/` — a workspace can mix modes, but that is not the same claim as universal TP-only posture.
- `registry_tp_only_state_must_be_imported_not_assumed/` — imported registry state must stay distinct from repo-local policy text.
- `reusable_workflow_release_needs_route_receipt_not_just_caller_filename/` — direct and reusable workflow identity routes need separate receipts.
- `gitlab_route_or_tp_mode_change_requires_authorization_drift_review/` — route or TP-only posture changes should produce explicit authorization drift.
- `portable_bundle_keeps_registry_route_and_rehearsal_separate/` — a support bundle should carry registry state, route receipts, and rehearsal separately.

The point of this fixture pack is to stop future passes from flattening:

- provider support,
- trusted-publisher claim route,
- trigger policy,
- publish mode,
- and rehearsal result

into one fake “trusted publishing is configured” story.

The added artifact-completeness pass also resists flattening:

- imported registry trust state,
- workflow-route identity,
- authorization drift across releases,
- and portable redacted review bundles

into one fake “the release path is still authorized” story.
