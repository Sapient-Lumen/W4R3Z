# Compile iteration feedback invalidation plan — 2026-03-23

This note sharpens **P-0537 Compile Iteration Feedback Kit** into the next buildable slice after reload-surface / restart-ceiling / readiness-class work.

## The sharper product question

If somebody started building **P-0537** this week, what should version `0.1` now provide so another engineer can tell **why** an edit stayed on the fast path or fell off it?

## Main answer

The next slice should add two first-class artifacts:

1. `edit-scope.receipt.json`
2. `fast-path-barrier.report.json`

Those artifacts should sit above watchers, linkers, hotpatch engines, frontend dev servers, and future relink substrate.
They should not try to replace those tools.
They should classify and export their consequences.

## `edit-scope.receipt.json`

This receipt should answer:

- what artifact family changed;
- what semantic class the change belongs to;
- what topology scope it lives in;
- whether the public interface changed;
- and how strong the evidence is.

### Minimal fields

- `artifact_scope` — `rsx_markup`, `css_asset`, `static_asset`, `rust_function_body`, `rust_type_layout`, `public_api_surface`, `global_or_static`, `thread_local`, `build_or_config`, `dependency_crate`, `workspace_peer_crate`, `unknown`
- `semantic_change_class` — `presentation_only`, `implementation_only`, `interface_affecting`, `layout_affecting`, `runtime_global_affecting`, `tooling_route_affecting`, `mixed`, `unknown`
- `topology_scope` — `tip_crate`, `local_dependency_crate`, `workspace_peer`, `transitive_dependency`, `frontend_only`, `mixed_frontend_and_rust`, `unknown`
- `interface_impact_class` — `public_interface_preserved`, `public_interface_changed`, `not_applicable`, `unknown`
- `confidence_class` — `direct_observation`, `imported_substrate`, `conservative_inference`, `manual_review`

## `fast-path-barrier.report.json`

This report should answer:

- what strongest fast route is still honest;
- what barrier blocked a stronger claim;
- what fallback remains;
- what readiness class the user should expect;
- and where manual review still begins.

### Minimal fields

- `strongest_available_route` — `visual_reload`, `frontend_hmr`, `rust_hotpatch`, `relink_only`, `full_rebuild_restart`, `manual_review`
- `barrier_class` — `frontend_only_surface`, `outside_tip_crate`, `public_interface_change`, `layout_or_alignment_change`, `global_initializer_change`, `thread_local_reset_risk`, `workspace_cascade_rebuild`, `build_config_or_module_route_change`, `state_reinstancing_required`, `unknown`
- `fallback_class` — `keep_fast_path`, `downgrade_to_visual_only`, `relink_but_do_not_patch`, `restart_with_state_reset`, `restart_with_reinstancing`, `manual_review`
- `readiness_class` — `visual_update_visible`, `logic_ready_without_restart`, `restart_complete`, `not_achieved`, `manual_review`
- `confidence_class` — `direct_observation`, `imported_substrate`, `conservative_inference`, `manual_review`

## Real framework proving grounds

### 1. Dioxus + `subsecond`

The archive should prove it can keep these separate:
- RSX or asset changes that stay on a visual fast path;
- Rust logic edits that can hotpatch in the tip crate;
- dependency/workspace edits that fall outside current patch visibility;
- globals/statics/TLS edits with claim ceilings;
- struct-layout edits that require reinstancing or restart.

### 2. Browser-first routes (`trunk`, cargo-leptos)

The archive should prove it can keep these separate:
- CSS-only update;
- browser live reload;
- Rust logic compile/reload;
- and “fast visible feedback” that is not the same as “logic-ready fast path.”

### 3. Mixed desktop routes (Tauri)

The archive should prove it can keep these separate:
- frontend dev-server path;
- Rust rebuild / rerun path;
- and the fact that both may coexist without becoming one fake universal reload surface.

### 4. Upstream relink aspirations

The archive should prove it can say:
- “interface preserved”;
- “today still cascades rebuilds”;
- and “should become relink-only if upstream substrate matures.”

That is exactly the kind of crate-shaped truth another team could consume.

## What version `0.1` should provide other people

1. one edit-scope receipt per captured edit;
2. one fast-path barrier report per attempted dev-loop claim;
3. one doctor command that rejects overclaims like “hot reload works” when the route was only CSS/browser-visible or when the edit class is outside the hotpatch ceiling;
4. one portable bundle that joins edit scope, barrier cause, surface route, restart plan, state continuity, and readiness class;
5. one way to diff two bundles so teams can see whether a framework, linker, or workspace reshaping actually widened or narrowed the fast path.

## Recommended CLI growth

- `cargo iterate scope --paths <changed paths...>`
- `cargo iterate barriers --bundle <bundle>`
- `cargo iterate diff old new`

Do **not** start by trying to perform the hotpatch itself.
Start by exporting the truth about the route and the barrier.

## Guardrail

Do not let future passes flatten these into one fake “the edit stayed fast” story:

1. edit scope,
2. interface impact,
3. barrier cause,
4. fallback class,
5. readiness class.
