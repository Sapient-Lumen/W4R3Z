# Cargo Script Workbench Kit fixtures

This fixture family exists to make **P-0435 Cargo Script Workbench Kit** less abstract.

The point is not to reimplement Cargo.
The point is to standardize one small single-file-package bundle another maintainer can review.

## Core bundle files

- `script-manifest.view.json`
- `script.lock.json`
- `script.receipt.json`
- `script-doctor.report.json`
- optional `script-export.plan.json`
- optional `script-portability.diff.json`
- `notes.md`

## Scenario families

### `hashed_target_dir_lockfile`
Proves that single-file packages use a hashed target-dir lane under Cargo home and place the lockfile there.
The bundle should preserve those locations explicitly rather than pretending the script has an ordinary workspace root.

### `omitted_edition_warning`
Proves that Cargo can infer an edition for a single-file package.
The bundle should record that this was defaulted and surface portability guidance rather than hiding it.

### `parent_config_without_workspace_discovery`
Proves that workspace auto-discovery can stay disabled while config influence is still relevant.
The bundle should keep those facts separate.

## Design guardrails

- Keep inferred manifest fields separate from explicit frontmatter.
- Preserve target-dir choice and lockfile location explicitly.
- Keep workspace auto-discovery state separate from parent config influence.
- Prefer short doctor verdicts plus `manual_review_required` over fake certainty.


## 2026-03-22 artifact-rich additions

This pass promotes a sharper support-contract layer above the older `script.*` bundle files.

### New first-class artifacts

- `frontmatter-authority.receipt.json`
- `discovery-scope.receipt.json`
- `invocation-interpretation.receipt.json`
- `cache-residency.receipt.json`
- `export-lineage.plan.json`
- `script-support-bundle.manifest.json`

### New scenario families

#### `embedded_manifest_defaults_need_authority_not_guessing`
Proves that explicit frontmatter, inferred defaults, and disallowed fields must stay separate.

#### `manifest_command_changes_config_root_and_verbosity`
Proves that `cargo <path>` must not be flattened into `cargo run --manifest-path <path>`.

#### `workspace_autodiscovery_disabled_but_parent_config_still_influences`
Proves that disabled workspace auto-discovery does not mean parent config influence vanished.

#### `hashed_target_dir_and_lockfile_need_cache_residency_receipt`
Proves that target-dir / lockfile placement are portable handoff facts, not incidental cache trivia.

#### `export_to_multifile_package_requires_lineage_and_choices`
Proves that script export must preserve naming/defaulting/provenance and record human choices.

#### `support_bundle_joins_authority_scope_and_export`
Proves that a single support bundle can connect script semantics, discovery truth, and export planning.
