# Compile iteration feedback — framework lattice (2026-03-23)

This note sharpens **P-0537 Compile Iteration Feedback Kit** around real framework families.

## Main judgment

The crate should not try to erase framework differences.
It should make them comparable.

A serious implementation should therefore model compile-iteration workflows as a lattice of **routes** and **claim ceilings**, not as one fake “hot reload” flag.

## The practical families the crate should compare

### 1. UI-structure reload without Rust recompilation

Examples:
- Dioxus RSX hot reload
- Dioxus string-attribute updates
- immediate CSS-only refresh routes

What the crate should export:
- `reload-surface.report.json`
- `patch-eligibility.report.json`
- `latency-budget.report.json`

What the crate must not imply:
- general Rust logic patching
- state migration proof
- dependency-workspace-wide edit support

### 2. Asset or stylesheet live update

Examples:
- Dioxus asset hot reload
- Trunk / cargo-leptos visible CSS updates

What the crate should export:
- surface = `css_asset` or `static_asset`
- ready class = `asset_update_visible`
- budget measured to visual readiness, not full logic readiness

What the crate must not imply:
- Rust code iteration is equally fast
- backend or process state continuity has been proven

### 3. Experimental Rust hotpatch / in-place logic replacement

Examples:
- Dioxus `dx serve --hotpatch`
- future Subsecond-like integrations

What the crate should export:
- `patch-eligibility.report.json`
- `reload-surface.report.json`
- `state-continuity.contract.json`
- `fallback-restart.plan.json`

What the crate must keep explicit:
- edit classes still outside the patch envelope
- workspace/dependency-edit gaps
- global / initializer / signature ceilings

### 4. Rust reload plus frontend devserver route

Examples:
- Tauri `tauri dev` plus `build.devUrl` / `beforeDevCommand`

What the crate should export:
- one route for frontend devserver / HMR posture
- one route for Rust rebuild / reload posture
- one `reload-surface` classification that says these are adjacent but distinct

What the crate must not imply:
- frontend HMR automatically proves Rust feedback speed
- Rust hot-reload automatically proves frontend-state continuity
- the composite flow has one simple state story

### 5. Plain watcher + rebuild + restart loops

Examples:
- simple `cargo run` watcher workflows
- service and CLI restart loops

What the crate should export:
- restart fallback as a first-class success case
- honest latency-budget measurements
- no embarrassment about `full_rebuild_restart`

What the crate must not imply:
- restart-free development is required for the crate to be useful

## Recommended artifact mapping

| Workflow family | Must-have artifacts |
|---|---|
| UI-only reload | reload-surface, patch-eligibility, latency-budget |
| Asset/CSS reload | reload-surface, latency-budget |
| Rust hotpatch | patch-eligibility, reload-surface, state-continuity, fallback-restart, latency-budget |
| Tauri mixed route | reload-surface, fallback-restart, latency-budget |
| Watch/restart | fallback-restart, latency-budget |

## The stronger product thesis after this pass

The crate is valuable when another engineer can open one bundle and answer:

1. **What surface changed?**
2. **Did Rust code recompile?**
3. **Was the result visual-only, logic-ready, or restart-ready?**
4. **Which edits still force rebuild or restart?**
5. **What budget did the workflow hit or miss?**

## Boundary reminder

P-0537 is not:
- Dioxus,
- Tauri,
- Trunk,
- cargo-leptos,
- a linker,
- or a watcher.

It is the **portable decision and evidence layer above them**.

## Sources

- https://dioxuslabs.com/learn/0.7/essentials/ui/hotreload/
- https://dioxuslabs.com/learn/0.7/tutorial/rsx/
- https://v2.tauri.app/reference/cli/
- https://book.leptos.dev/interlude_styling.html
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
