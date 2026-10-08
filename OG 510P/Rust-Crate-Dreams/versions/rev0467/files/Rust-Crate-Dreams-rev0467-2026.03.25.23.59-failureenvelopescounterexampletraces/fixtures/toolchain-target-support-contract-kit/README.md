# Toolchain & Target Support Contract Kit fixtures

These fixtures are for **support-contract** artifacts, not docs.rs failure replay.
They should answer “what do we claim to support, what did we actually observe, and what drifted?”

Also consult `meta/toolchain-target-support-lane-boundaries-2026-03-22.md`, `meta/toolchain-target-support-artifact-route-boundaries-2026-03-22.md`, and `meta/toolchain-target-support-authority-surface-plan-2026-03-22.md` so imported upstream authority, project support class, public docs surface, prerequisites, exercise scope, artifact route, and host-vs-target topology stay separate.

Scenario families in this pass:
- `docsrs_default_target_drift_after_2025_change/`
- `minimal_profile_missing_dev_components/`
- `path_toolchain_ignores_components_and_targets/`
- `compile_only_target_missing_linker/`
- `virtual_workspace_resolver3_msrv_split/`
- `cross_target_runner_required_for_tests/`
- `official_rustup_host_exists_but_project_unclaimed/`
- `env_override_masks_repo_pin/`
- `nightly_component_fallback_changes_effective_channel/`
- `explicit_target_build_splits_host_helper_scope/`
- `tier2_target_needs_no_std_and_last_known_os_baseline/`

- `cargo_build_dir_layout_v2_breaks_target_dir_spelunking/`
- `proc_macro_and_runner_live_on_host_even_when_target_is_cross/`
- `target_tier_demotion_requires_project_support_restatement/`

New artifact families in this pass:
- `upstream-support-authority.import.json`
- `public-docs-surface.receipt.json`
- `toolchain-support-bundle.manifest.json`

Additional scenario families in this pass:
- `portable_bundle_keeps_imported_authority_docs_surface_and_local_contract_separate/`
