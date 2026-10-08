# Cargo Workspace Boundary Doctor Kit fixtures

This fixture family exists to make **P-0506 Cargo Workspace Boundary Doctor Kit** less abstract.

The point is not to reimplement Cargo discovery.
The point is to standardize one small boundary bundle another maintainer can review.

## Core bundle files

- `boundary-context.toml`
- `discovery-trace.receipt.json`
- `workspace-membership.report.json`
- `config-probe.report.json`
- `ancestor-discovery.receipt.json`
- `config-layering.report.json`
- `invocation-mode.report.json`
- `boundary-diagnosis.report.json`
- optional `boundary-diff.report.json`
- optional `boundary-support-bundle.manifest.json`
- `invocation-advice.md`
- `notes.md`

## Scenario families

### `parent_home_manifest_poisoning`
Proves that a parent manifest can become a surprising workspace boundary.
The bundle should capture which parents were probed and classify the result conservatively.

### `manifest_path_local_config_split`
Proves that `--manifest-path` and the current working directory can disagree about which config files matter.
The bundle should keep target-project selection and config probing separate.

### `parent_config_include_chain_and_cli_override_need_distinct_layer_receipts`
Proves that a file-layer view is not enough: include edges, env/CLI overrides, and path-basis rules can change the effective config story.
The bundle should keep ancestor discovery and config layering as separate review objects.

### `manifest_command_and_manifest_path_have_different_config_roots`
Proves that manifest-command mode and `--manifest-path` should not be flattened into one invocation route.
The bundle should capture config-root expectations explicitly.

### `single_file_package_disables_workspace_autodiscovery_but_not_config_discovery`
Proves that a `.rs` single-file package lane can disable workspace auto-discovery without making config discovery disappear.
The bundle should not blur those into one “no discovery happened” story.

## Design guardrails

- Keep workspace membership, ancestor discovery, config layering, and invocation mode as separate reports.
- Preserve current working directory, subject path, and manifest-command posture explicitly.
- Prefer short advice plus `manual_review_required` over fake certainty.
