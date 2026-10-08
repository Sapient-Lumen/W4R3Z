# MSRV Workspace Lab fixtures

This fixture family exists to make **P-0036 MSRV Workspace Lab** implementation-shaped.

The point is not to claim one magic repo-wide minimum compiler.
The point is to standardize one small bundle another maintainer can review.

## Core bundle files

- `msrv-policy.toml`
- `policy-activation.receipt.json`
- `effective-workspace-promise.manifest.json`
- `toolchain-matrix.plan.json`
- `msrv-observation.receipt.json`
- `command-family-floor.report.json`
- `lockfile-floor.receipt.json`
- `msrv-blame.report.json`
- optional `resolver-lane.diff.json`
- optional `policy-split-diff.report.json`
- optional `msrv-support-bundle.manifest.json`
- `adoption-plan.md`
- `notes.md`

## Scenario families

### `mixed_workspace_policy_split`
Proves that not every workspace should publish one MSRV promise:
- a library may need to stay low,
- a CLI or examples lane may float higher,
- and the right output is a policy split plus an `effective-workspace-promise.manifest.json`, not a fake single number.

### `inactive_target_edge_metadata_break`
Proves that a green build is not the whole MSRV story:
- an inactive target-specific dependency edge can still change metadata or review surfaces,
- the bundle must record command family and target lane explicitly,
- and the blame report should not overclaim that the main product lane is broken when it is only pressured.

### `virtual_workspace_needs_workspace_resolver3_to_activate_fallback_policy`
Proves that a member edition or local expectation is not enough to activate resolver v3 for a virtual workspace root:
- the bundle must capture expected versus observed policy,
- and the receipt must say where the active policy really came from.

### `lockfile_v4_update_path_can_raise_authoring_floor_without_raising_build_floor`
Proves that an old/pinned build lane and an ongoing lockfile-authoring lane are not the same promise:
- the bundle must record lockfile version and authoring action,
- and the command-family report must keep `build` support separate from `update` / `package` / `generate-lockfile` support.

## Design guardrails

- Keep declared policy and observed floors separate.
- Preserve which Cargo resolver policy was active.
- Distinguish build, metadata, doc, update, and package command families.
- Keep pinned-lockfile buildability separate from lockfile-authoring compatibility.
- Prefer `manual_review_required` over a fake universal MSRV number.


## New artifact-completeness emphasis

This fixture family now also treats the following as first-class review objects:

- `effective-workspace-promise.manifest.json` — normalized per-member support promises after inheritance and split policy.
- `policy-split-diff.report.json` — revision-to-revision drift when only one member or command-family promise changed.
- `msrv-support-bundle.manifest.json` — one portable bundle for declared policy, activation, command-family floors, lockfile floor, and explicit manual-review gaps.

## New scenario families

### `virtual_workspace_resolver_expectation_needs_activation_receipt`
Proves that a virtual workspace can expect fallback but still fail to activate it without an explicit root resolver setting.

### `mixed_workspace_library_stays_low_cli_moves_higher_needs_effective_promise`
Proves that the public library promise may stay lower than the CLI/examples promise and should be exported as a normalized member map.

### `inactive_target_edge_keeps_build_green_but_metadata_floor_higher`
Proves that command-family truth can diverge without overclaiming that the shipped build lane is broken.

### `lockfile_update_floor_rises_but_pinned_build_lane_stays_supported`
Proves that building from an existing lockfile and authoring/updating that lockfile are different support promises.

### `release_changes_only_cli_member_promise_not_library_baseline`
Proves that member-granularity drift and portable review bundles are more honest than one repo-wide MSRV number.
