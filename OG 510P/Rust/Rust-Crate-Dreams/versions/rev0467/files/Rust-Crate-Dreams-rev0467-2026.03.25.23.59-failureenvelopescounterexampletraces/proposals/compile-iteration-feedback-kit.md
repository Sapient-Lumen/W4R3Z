---
id: P-0537
title: Compile Iteration Feedback Kit — coverage-scope/claim-ceiling receipts, patch-eligibility and live-update truth, activation/generation/retirement truth, and restart-fallback bundles
status: idea
domains: [tooling, dx, performance, gui, games, services, live-reload, cargo]
last_reviewed: 2026-03-23
evidence:
  - https://blog.rust-lang.org/2026/03/20/rust-challenges/
  - https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
  - https://blog.rust-lang.org/2025/09/01/rust-lld-on-1.90.0-stable/
  - https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
  - https://docs.rs/subsecond
  - https://dioxuslabs.com/learn/0.7/essentials/ui/hotreload/
  - https://dioxuslabs.com/learn/0.7/tutorial/rsx/
  - https://github.com/davidlattimore/wild
  - https://docs.rs/crate/cargo-watch/latest/source/README.md
  - https://v2.tauri.app/reference/cli/
  - https://book.leptos.dev/interlude_styling.html
  - https://docs.rs/hot-lib-reloader-macro/latest/hot_lib_reloader_macro/
  - https://docs.rs/bevy_simple_subsecond_system/latest/bevy_simple_subsecond_system/
  - https://docs.rs/bevy_simple_subsecond_system/latest/bevy_simple_subsecond_system/migration/
  - https://docs.rs/bevy_simple_subsecond_system/latest/bevy_simple_subsecond_system/hot_patched_app/trait.HotPatchedAppExt.html
---

# Problem

Rust now has several promising answers to the edit-compile-run tax, but they are fragmented enough that teams still have to build the overall workflow from folklore.

Fresh official signals make this gap unusually concrete:

- the Rust challenges write-up says compile performance is the **universal productivity tax** and calls out GUI teams living with 8–10 second feedback loops;
- the same write-up explicitly points to hot reloading and faster linking as high-leverage mitigations;
- the compiler-performance survey says incremental rebuilds after small changes remain one of the sharpest workflow pains;
- Rust 1.90 switched `x86_64-unknown-linux-gnu` to LLD by default because linking time mattered enough to move upstream policy;
- the `relink-don't-rebuild` goal exists because public-interface-preserving edits still trigger too much downstream rebuilding;
- and emerging runtime hotpatch substrate such as `subsecond`, plus framework-local hot reload in Dioxus, proves that “faster local iteration” is no longer fantasy.

What is still missing is **not** another file watcher, another linker, or another framework-local hot reload feature.

The missing crate is a **compile-iteration support contract** that helps other people answer:

- which edits can hot-reload or hot-patch,
- what exact routes, libraries, systems, or exports are actually under coverage,
- where support claims must stop,
- which edits still require relink or full restart,
- what linker or relink route was actually used,
- what state continuity story is being claimed,
- when fresh code actually becomes active,
- what old code may remain reachable,
- what generation of code a given route is believed to be running,
- whether mixed-generation execution is still possible,
- what actually happened when a live update attempt ran,
- what degraded operating mode the current session is honestly in,
- what restart fallback is required when patchability breaks,
- whether the measured loop actually met the intended latency budget,
- when old generations are expected to retire,
- and whether old-generation work has actually drained.

# What it provides

Core artifacts:

- `iteration-profile.toml` — latency budget, target lane, watcher assumptions, linker preferences, patch-safety policy, and restart policy.
- `edit-event.receipt.json` — normalized description of the source change, crate/module scope, and triggering route.
- `coverage-scope.receipt.json` — what surfaces, crates, routes, or exports are actually under the live-update regime.
- `coverage-ceiling.report.json` — what support claims are explicitly out of bounds because coverage is tip-crate-only, annotation-only, wrapper-only, launch-time-only, or target-bound.
- `edit-scope.receipt.json` — what the edit actually touched: markup, asset, function body, interface, layout, globals/TLS, build/config route, or dependency/workspace code.
- `patch-eligibility.report.json` — whether the change is `ui_only_reload`, `asset_reload`, `function_hotpatch`, `relink_only`, `full_rebuild_restart`, or `manual_review_required`, plus why.
- `linker-route.receipt.json` — which linker/relink path actually ran, where the choice came from, and whether the route only reduced link time or also enabled patch-friendly output.
- `reload-surface.report.json` — what surface was actually live-updated: markup, assets, functions, symbols, generated code, or none.
- `fast-path-barrier.report.json` — why a stronger fast path was unavailable: outside tip crate, interface change, layout hazard, globals/TLS ceiling, workspace cascade, or frontend-only route.
- `state-continuity.contract.json` — which state classes are preserved, reset, migrated, or out of scope.
- `activation-boundary.report.json` — when fresh code actually becomes active: immediately, at the next reloadable entrypoint, after an explicit handoff boundary, or only after restart.
- `stale-code-risk.report.json` — what old code/identity routes may remain reachable after reload: stored function pointers, trait objects, in-flight frames, thread-local copies, or identity-sensitive registries.
- `retirement-boundary.report.json` — when older code is expected to stop being reachable for a route class, and what boundary supports that claim.
- `old-generation-drain.report.json` — whether pre-reload frames, callbacks, or queued work were actually observed drained, partially rewound, or remain unknown.
- `live-update-outcome.report.json` — what actually happened when a patch/reload attempt ran: applied, rejected, failed, restart-required, crashed/unknown, or old-code-retained.
- `degraded-iteration-mode.report.json` — whether the current process is healthy, degraded-but-running, observe-only, restart-only, disabled, or crashed/unknown for further iteration.
- `fallback-restart.plan.json` — quiesce hooks, restart steps, cache/session restore, and manual-review gates when a live update is not safe.
- `latency-budget.report.json` — measured edit-to-visible-feedback timing against the declared budget.
- `iteration-support-bundle.manifest.json` — portable bundle joining the above artifacts for review, support, or benchmark comparison.
- optional `notes.md` — compact explanation for PRs, issue reports, and local iteration docs.

CLI surface:

- `cargo iterate profile init`
- `cargo iterate classify --edit edit-event.receipt.json`
- `cargo iterate measure --cmd "cargo run"`
- `cargo iterate doctor`
- `cargo iterate bundle`
- `cargo iterate diff old-bundle new-bundle`

# What the crate should provide other people

1. **One coverage-scope receipt** instead of hand-wavy “hot reload is supported.”
2. **One coverage-ceiling report** instead of burying tip-crate / annotation / wrapper / launch-time gaps in prose.
3. **One honest patch-vs-restart answer** instead of hand-wavy “hot reload works.”
4. **One edit-scope receipt** so another engineer can tell what kind of change was actually made.
5. **One fast-path barrier report** so a route failure does not get summarized as mere bad luck.
6. **One linker-route receipt** instead of vague “it felt faster after we changed the linker.”
7. **One state continuity contract** instead of hidden assumptions about globals, tasks, caches, or in-memory documents.
8. **One activation-boundary report** so another engineer can see when fresh code is actually live.
9. **One stale-code-risk report** so stored call routes or identity drift are not mistaken for full takeover.
10. **One generation-witness report** so another engineer can see what code epoch is actually being claimed for a route or library.
11. **One mixed-generation-risk report** so “new build loaded” does not masquerade as homogeneous execution.
12. **One retirement-boundary report** so “new code is reachable” does not masquerade as “old code is retired.”
13. **One old-generation-drain report** so reload lifecycle events do not masquerade as drain completeness.
14. **One live-update-outcome report** so another engineer can tell whether the attempted update actually applied or merely looked patchable.
15. **One degraded-iteration-mode report** so warnings, crashes, and “still running but not trustworthy” posture are explicit.
16. **One restart fallback plan** instead of ad-hoc shell scripts and tribal knowledge.
17. **One latency-budget report** that says whether the actual loop meets the intended workflow bar.
18. **One portable support bundle** that another engineer can inspect without reproducing the exact local setup.
19. **One framework-neutral decision layer** above watchers, linkers, runtime hotpatchers, and future upstream relink work.

# Persona / who it’s for

- GUI and game developers chasing faster visible feedback
- service teams with long-running processes that would benefit from safe function patching
- framework/tool authors trying to expose iteration workflows without overclaiming
- build/perf engineers trying to explain where latency really comes from

# Users & user stories

- **GUI developer**: “Tell me whether this edit can use UI-only reload, runtime hotpatch, or needs a full rebuild.”
- **Game engine author**: “Attach one bundle to a dev-tools issue showing the patch route, preserved state, and fallback path.”
- **Backend engineer**: “Measure whether switching from the system linker to LLD or Wild actually improved the edit-to-ready budget.”
- **Framework maintainer**: “Be explicit about which edits are hotpatch-safe and which force restart because globals, generated code, or type layout changed.”

# Prior art (and why it’s insufficient)

- **Watchexec / Bacon / cargo-watch** help trigger commands after file changes, but they do not classify patchability, state continuity, or restart truth.
- **Dioxus RSX hot reload** is excellent for markup-level UI edits, but it is intentionally narrower than a general Rust code-iteration contract.
- **`subsecond`** makes runtime hot-patching and thin-linking more real, but it does not itself define a portable artifact pack for support, review, or cross-framework comparison.
- **LLD** and **Wild** improve linking speed, but a faster linker is not the same thing as a safe hotpatch route or a state continuity promise.
- **`relink-don't-rebuild`** is an important upstream direction, but it is still experimental and still not the receiver-facing artifact layer teams need right now.

# Design goals

1. **Latency-first** — optimize for the edit-to-feedback loop, not only compile-step timing.
2. **Surface separation** — keep watcher, compile, link, patch, reload, and restart lanes distinct.
3. **Framework-neutral** — support UI frameworks, long-running services, game loops, and tool UIs without hard-coding one stack.
4. **State-honest** — preserving function code is not the same thing as preserving process state safely.
5. **Artifact-first** — emit small receipts and reports before chasing dashboards.
6. **Generation-honest** — distinguish route-level code epochs from mere build/reload completion.
7. **Future-compatible** — import future upstream relink/reuse substrate without pretending it already solves restart, state, or generation truth.
8. **Conservative by default** — prefer `manual_review_required` over unsafe optimism.

# MVP surface

Minimal types:
- `IterationProfile`
- `EditEventReceipt`
- `CoverageScopeReceipt`
- `CoverageCeilingReport`
- `EditScopeReceipt`
- `PatchEligibilityReport`
- `FastPathBarrierReport`
- `LinkerRouteReceipt`
- `ReloadSurfaceReport`
- `StateContinuityContract`
- `ActivationBoundaryReport`
- `StaleCodeRiskReport`
- `GenerationWitnessReport`
- `MixedGenerationRiskReport`
- `RetirementBoundaryReport`
- `OldGenerationDrainReport`
- `LiveUpdateOutcomeReport`
- `DegradedIterationModeReport`
- `FallbackRestartPlan`
- `LatencyBudgetReport`
- `IterationSupportBundleManifest`

Minimal functions:
- `capture_edit_event()`
- `capture_coverage_scope()`
- `classify_coverage_ceiling()`
- `classify_edit_scope()`
- `classify_patch_eligibility()`
- `classify_fast_path_barrier()`
- `capture_linker_route()`
- `capture_reload_surface()`
- `build_state_continuity_contract()`
- `classify_activation_boundary()`
- `classify_stale_code_risk()`
- `build_generation_witness()`
- `classify_mixed_generation_risk()`
- `classify_retirement_boundary()`
- `classify_old_generation_drain()`
- `plan_restart_fallback()`
- `measure_latency_budget()`
- `write_bundle()`

Feature flags:
- `watchers`
- `dioxus-import`
- `subsecond-import`
- `linker-route`
- `serde`
- `bundle`

# Compatibility story

- Starts by importing existing local tooling and framework behavior rather than replacing it.
- Supports plain “watch and restart” workflows as first-class outputs, not only sexy live-patch paths.
- Keeps room for future upstream relink/rebuild improvements and linker evolution.
- Degrades honestly when patchability or state continuity cannot be proven.

# Conformance & fixtures

The fixture pack should freeze at least these scenarios:

- UI-only markup reload with no Rust-code rebuild.
- faster-linker route that improves latency but does **not** imply hotpatch capability.
- function-level patch path that preserves some state classes but excludes globals/layout-sensitive changes.
- static-layout or constructor change that requires explicit restart fallback.
- retirement-boundary case where one route is known to retire after unwind/reentry while whole-process drain stays unknown.
- portable support bundle that keeps patch truth, linker truth, state truth, activation truth, generation truth, retirement truth, and drain truth separate.

# Path to boring stability

- Stabilize `patch-eligibility`, `state-continuity`, `activation-boundary`, `stale-code-risk`, `generation-witness`, `retirement-boundary`, `old-generation-drain`, and the bundle manifest before adding many framework adapters.
- Start with capture/classify/measure/export, not orchestration-heavy runtime control.
- Keep patchability classification explicit enough that teams can review it in code review and local docs.
- Treat state migration hooks as optional imports, not a hidden requirement.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A cargo subcommand and library that record one edit event, classify patchability, capture linker route, record state continuity, classify live-update outcome and degraded mode, retain a restart fallback, measure the latency budget, and emit one portable bundle.

# De-risk plan

1. Start with classification and receipts rather than automated patch orchestration.
2. Import watcher/framework/linker facts conservatively and preserve provenance.
3. Keep state continuity a first-class contract from day one.
4. Add framework-specific adapters only after the neutral artifact pack proves useful.

# Non-goals

- Not a replacement for Rustc, Cargo, Watchexec, Bacon, LLD, Wild, Dioxus, or `subsecond`.
- Not a promise that every Rust edit can become hotpatch-safe.
- Not a generic benchmarking dashboard.
- Not a hidden process supervisor with opaque restart semantics.
- Not a claim that faster linking alone solves the iteration loop.

# Architecture & API sketch

```rust
pub fn capture_edit_event(cx: &EditCaptureContext) -> Result<EditEventReceipt>;
pub fn classify_patch_eligibility(
    profile: &IterationProfile,
    edit: &EditEventReceipt,
    substrate: &ObservedIterationSubstrate,
) -> Result<PatchEligibilityReport>;
pub fn capture_linker_route(cx: &LinkerCaptureContext) -> Result<LinkerRouteReceipt>;
pub fn build_state_continuity_contract(
    profile: &IterationProfile,
    patch: &PatchEligibilityReport,
) -> Result<StateContinuityContract>;
pub fn classify_activation_boundary(
    profile: &IterationProfile,
    patch: &PatchEligibilityReport,
    substrate: &ObservedIterationSubstrate,
) -> Result<ActivationBoundaryReport>;
pub fn classify_stale_code_risk(
    profile: &IterationProfile,
    substrate: &ObservedIterationSubstrate,
) -> Result<StaleCodeRiskReport>;
pub fn classify_live_update_outcome(
    profile: &IterationProfile,
    substrate: &ObservedIterationSubstrate,
) -> Result<LiveUpdateOutcomeReport>;
pub fn classify_degraded_iteration_mode(
    profile: &IterationProfile,
    substrate: &ObservedIterationSubstrate,
) -> Result<DegradedIterationModeReport>;
pub fn measure_latency_budget(cx: &LatencyMeasureContext) -> Result<LatencyBudgetReport>;
pub fn write_bundle(bundle: &IterationSupportBundle, out: &Path) -> Result<()>;
```

Bundle draft:

- `iteration-profile.toml`
- `edit-event.receipt.json`
- `edit-scope.receipt.json`
- `patch-eligibility.report.json`
- `fast-path-barrier.report.json`
- `linker-route.receipt.json`
- `reload-surface.report.json`
- `state-continuity.contract.json`
- `activation-boundary.report.json`
- `stale-code-risk.report.json`
- `fallback-restart.plan.json`
- `latency-budget.report.json`
- `iteration-support-bundle.manifest.json`
- `notes.md`

# Security / safety model

- Treat live patch routes as capability claims that require explicit evidence.
- Preserve provenance for watcher, linker, and hotpatch imports.
- Keep state-preservation claims conservative around globals, constructors, TLS, and generated code.
- Avoid silent code injection or process control in the MVP.

# Maintenance & governance plan

- Keep the neutral artifact vocabulary small and versioned.
- Treat adapters to Dioxus, `subsecond`, or future relink substrate as optional layers.
- Maintain a fixture pack that forces sharp lane boundaries between speedups, patchability, and restart truth.
- Prefer importer modularity over one giant runtime-integrated crate.


# 2026-03-23 framework-lattice addendum

A buildable next slice should now compare at least these real route families explicitly:

1. **Dioxus RSX / asset reload** — fast visible feedback that should stay separate from Rust logic patching.
2. **Dioxus `--hotpatch`** — broader logic updates with explicit ceilings around globals, initializers, signatures, and dependency/workspace edits.
3. **Tauri `tauri dev`** — composite route where Rust reload and frontend devserver posture coexist but should not be flattened into one support claim.
4. **Trunk / cargo-leptos CSS-visible updates** — useful immediate browser feedback that should be measured as a visual budget, not a broad Rust logic budget.

That means the fixture pack must now treat these as first-class:
- `reload-surface.report.json`
- `fallback-restart.plan.json`
- `latency-budget.report.json`

and should not stop at `patch-eligibility`, `linker-route`, and `state-continuity` alone.


# 2026-03-23 invalidation addendum

A buildable next slice should now compare at least these real barrier families explicitly:

1. **tip-crate visibility ceilings** — Dioxus / `subsecond` can patch logic in the tip crate but currently ignore dependency/workspace edits.
2. **layout / reinstancing ceilings** — struct-layout edits are not ordinary function-body hotpatches and need an explicit reinstancing or restart story.
3. **interface-preserving rebuild cascades** — current Cargo/rustc still rebuild more than users expect for some implementation-only edits, and that should be reported as a barrier class rather than vague slowness.
4. **frontend-only fast paths** — CSS/browser-visible updates should stay separate from Rust-logic fast-path claims.

That means the fixture pack must now treat these as first-class too:
- `edit-scope.receipt.json`
- `fast-path-barrier.report.json`

and should not stop at surface/restart/budget truth alone.


# 2026-03-23 activation / stale-code addendum

A buildable next slice should now compare at least these real takeover families explicitly:

1. **entrypoint-gated activation** — some systems only activate fresh code when a designated reloadable function is called, not at rebuild completion time.
2. **explicit handoff boundaries** — some systems require serialize/deserialize or reinitialization around reload events before continuity can be claimed honestly.
3. **stored-route stale code** — function pointers, trait objects, or similar call paths can keep old code alive after a reload-looking event.
4. **identity-sensitive continuity** — `TypeId`-keyed or similar systems may preserve payloads only through explicit rebinding rather than true same-identity continuity.

That means the fixture pack must now treat these as first-class too:
- `activation-boundary.report.json`
- `stale-code-risk.report.json`

and should not stop at edit scope / barrier / continuity truth alone.
