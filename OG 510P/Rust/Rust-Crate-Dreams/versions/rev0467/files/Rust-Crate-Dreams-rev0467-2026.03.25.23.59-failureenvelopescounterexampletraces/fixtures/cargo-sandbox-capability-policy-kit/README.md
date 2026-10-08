# Cargo Sandbox & Capability Policy Kit fixtures

These fixtures are for **P-0107 Cargo Sandbox & Capability Policy Kit**.

The point of this pack is to freeze the review layer above evolving compile-time sandbox substrate:

- policy authority,
- actor capability scope,
- enforcement mode,
- exception ownership,
- release-to-release policy drift,
- ambient input visibility,
- sanitization posture,
- and launcher-route honesty.

These fixtures should stay distinct from:

- runtime crate-authority packs,
- delegated build-unit topology receipts,
- proc-macro migration/readiness kits,
- host-vs-target support receipts,
- and generic OS sandbox runtimes.

Scenario families in this pass:
- `build_script_pkg_config_needs_path_grant_but_proc_macro_stays_deny/`
- `observe_mode_hides_enforcement_failure/`
- `shared_proc_macro_wrapper_means_granularity_is_partial/`
- `workspace_overlay_authorizes_break_glass_network/`
- `release_broadens_capability_scope_and_requires_review/`

Additional scenario families in this pass:
- `parent_env_requires_explicit_whitelist_and_path_story/`
- `host_flags_bleed_without_target_split_changes_actor_ingress/`
- `build_script_can_influence_later_proc_macro_wrapper_route/`
- `global_runner_config_rejects_project_local_opt_out/`
- `portable_bundle_joins_policy_capabilities_ingress_and_route/`
