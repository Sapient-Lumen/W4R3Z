# Compile Iteration Feedback Kit fixtures

This fixture family is for **P-0537 Compile Iteration Feedback Kit**.
Its purpose is not to build a universal hot-reload engine.
Its purpose is to make the first **edit-to-feedback support bundle** reviewable.

## Core bundle shape

- `iteration-profile.toml` — latency budget, watcher route, linker expectations, patch safety policy, restart policy
- `edit-event.receipt.json` — normalized change event and scope
- `coverage-scope.receipt.json` — what surfaces, crates, routes, or exports are actually under the live-update regime
- `coverage-ceiling.report.json` — what support claims are explicitly out of bounds
- `edit-scope.receipt.json` — what the edit actually touched and whether it preserved the public interface
- `patch-eligibility.report.json` — hot-reload / hotpatch / relink / rebuild / restart classification
- `linker-route.receipt.json` — actual linker or relink route and where it came from
- `reload-surface.report.json` — what surface was really updated
- `fast-path-barrier.report.json` — why the stronger fast path was unavailable and what fallback remained
- `state-continuity.contract.json` — what state survives, resets, migrates, or is out of scope
- `activation-boundary.report.json` — when fresh code actually becomes active
- `stale-code-risk.report.json` — what old code or identity routes may remain reachable after reload
- `generation-witness.report.json` — what code epoch a route/library is believed to run and how that claim is witnessed
- `mixed-generation-risk.report.json` — whether old and new generations may coexist across routes after reload
- `retirement-boundary.report.json` — when older code is expected to stop being reachable for a route class
- `old-generation-drain.report.json` — whether pre-reload work was actually observed drained or only partially rewound
- `live-update-outcome.report.json` — what actually happened when the attempted live update ran
- `degraded-iteration-mode.report.json` — what operating posture the session is honestly in now
- `fallback-restart.plan.json` — what deterministic fallback remains when live update is not safe
- `latency-budget.report.json` — measured edit-to-feedback timing against the intended budget
- `iteration-support-bundle.manifest.json` — portable support bundle that keeps those truths separate
- `notes.md` — compact scenario explanation

## Scenario families

- `rsx_markup_change_uses_ui_hot_reload_not_code_patch/` — UI-only markup reload should not masquerade as general Rust code hotpatching
- `wild_or_lld_speedup_is_not_same_as_runtime_patch_route/` — faster linking is not itself hotpatch support
- `static_layout_or_constructor_change_requires_restart_contract/` — globals/layout/constructors can force restart despite patch-friendly tooling
- `portable_bundle_keeps_patch_linker_and_state_truth_separate/` — bundle shape keeps speed, patchability, and continuity distinct
- `dioxus_rsx_and_assets_are_not_rust_hotpatch/` — Dioxus route families stay separate
- `dioxus_three_reload_surfaces_require_separate_coverage_claims/` — framework marketing should not flatten distinct live-update surfaces into one coverage claim
- `subsecond_tip_crate_and_call_anchor_limit_live_update_coverage/` — tip-crate and anchor participation bound honest coverage
- `chaud_feature_flag_and_hot_annotations_define_covered_routes/` — annotations in source do not imply active coverage
- `hot_lib_reloader_wrapped_dylib_exports_define_reload_coverage/` — wrapper/export surfaces bound what is really reloadable
- `bevy_simple_subsecond_preexisting_annotated_systems_bound_runtime_coverage/` — launch-time and project-shape limits define real support ceilings
- `portable_bundle_keeps_coverage_scope_and_claim_ceiling_separate/` — bundle shape now carries coverage truth too
- `dioxus_hotpatch_has_restart_ceilings/` — experimental Rust hotpatch still needs restart ceilings
- `tauri_dev_joins_frontend_devserver_and_rust_reload_without_flattening_them/` — frontend devserver posture and Rust reload posture stay distinct
- `trunk_or_cargo_leptos_css_live_update_is_visual_budget_not_logic_budget/` — browser-visible CSS feedback is not the same thing as Rust-logic readiness
- `portable_bundle_keeps_surface_restart_and_budget_separate/` — bundle shape keeps surface, restart, and budget truth distinct
- `dioxus_dependency_edit_falls_outside_tip_crate_hotpatch/` — edit topology can block hotpatch even for logic-only changes
- `subsecond_struct_layout_change_requires_reinstancing_or_restart/` — layout-affecting edits need a stronger barrier/fallback story
- `interface_preserving_private_edit_still_cascades_rebuilds_today/` — interface-preserving edits deserve their own barrier class even when current tooling still cascades rebuilds
- `portable_bundle_keeps_edit_scope_barrier_and_readiness_separate/` — bundle shape now carries invalidation truth too
- `chaud_hot_code_activates_at_annotated_entrypoints_not_as_global_switch/` — fresh code activation can be entrypoint-gated instead of global
- `hot_lib_reloader_reload_events_make_state_handoff_explicit_not_implicit/` — reload-event boundaries and handoff steps stay explicit
- `function_pointers_and_trait_objects_can_keep_old_code_alive_after_reload/` — old call routes can survive a reload event
- `typeid_identity_shift_breaks_simple_same_state_claims_after_reload/` — identity continuity is not the same as value continuity
- `portable_bundle_keeps_activation_continuity_and_stale_code_separate/` — bundle shape now carries takeover truth too
- `subsecond_pointer_versioning_is_not_precise_generation_identity/` — latest detour is not the same as precise route-level generation identity
- `subsecond_nested_calls_define_generation_cut_points_not_global_takeover/` — nested call boundaries can act as generation cut points
- `chaud_can_leave_mixed_old_and_new_code_routes_alive_after_reload/` — mixed generations can survive a successful reload
- `hot_lib_reloader_load_counter_names_library_generation_not_full_route_coverage/` — library generation naming is not the same thing as route coverage
- `portable_bundle_keeps_generation_activation_and_residency_separate/` — bundle shape now carries code-epoch truth too
- `subsecond_rewind_retires_only_to_next_hot_anchor_not_whole_process/` — one rewind boundary should not masquerade as total retirement
- `chaud_hot_reload_completion_does_not_bound_old_route_retirement/` — completed reload is not itself a retirement proof
- `hot_lib_reloader_before_after_events_bracket_reload_not_old_generation_drain/` — reload lifecycle markers are weaker than drain completeness
- `portable_bundle_keeps_generation_retirement_and_drain_separate/` — bundle shape now carries retirement/drain truth too
- `subsecond_patch_error_keeps_patch_route_possible_but_current_attempt_failed/` — patchability and current-attempt success stay separate
- `chaud_warn_and_error_levels_distinguish_degraded_from_broken_live_reload/` — warning-only degraded mode is weaker than healthy live update
- `hot_lib_reloader_signature_or_tracing_issue_demands_restart_or_disable/` — dangerous combinations demand stronger failure-mode posture
- `portable_bundle_keeps_eligibility_outcome_and_degraded_mode_separate/` — bundle shape now carries current operating mode too

## Schema starter set

- `coverage-scope.receipt.schema.json`
- `coverage-ceiling.report.schema.json`
- `edit-scope.receipt.schema.json`
- `patch-eligibility.report.schema.json`
- `linker-route.receipt.schema.json`
- `reload-surface.report.schema.json`
- `fast-path-barrier.report.schema.json`
- `state-continuity.contract.schema.json`
- `activation-boundary.report.schema.json`
- `stale-code-risk.report.schema.json`
- `generation-witness.report.schema.json`
- `mixed-generation-risk.report.schema.json`
- `retirement-boundary.report.schema.json`
- `old-generation-drain.report.schema.json`
- `live-update-outcome.report.schema.json`
- `degraded-iteration-mode.report.schema.json`
- `fallback-restart.plan.schema.json`
- `latency-budget.report.schema.json`
- `iteration-support-bundle.manifest.schema.json`
