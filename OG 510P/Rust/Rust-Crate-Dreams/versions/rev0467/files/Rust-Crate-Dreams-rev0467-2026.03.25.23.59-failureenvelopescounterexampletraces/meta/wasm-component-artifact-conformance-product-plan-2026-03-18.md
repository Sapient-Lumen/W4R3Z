# Wasm Component Artifact + Conformance Kit — product plan (2026-03-18)

This note sharpens **P-0206 Wasm Component Contract & Conformance ShipKit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps maintainers publish one reviewable answer to:

- which Rust target/runtime family they built for,
- which tooling path actually produced the component,
- what exact package/world/interface/version contract the component carries,
- whether imports are fully closed, partially bundled, or still host-supplied,
- how another person can exercise the component,
- and what changed between releases.

It should **not** try to become a replacement for Cargo, `cargo-component`, WAC, `wasm-tools`, `wit-bindgen`, or Wasmtime.
Those are substrate and workflow partners, not the missing product.

## Why this lane is finally believable

The substrate is now real enough to build on:

- current Rust component-model docs say `cargo-component` is being deprecated because native tooling can now be used directly; citeturn843414search0turn204112search0
- Rust’s 2026 goals explicitly call out Wasm Components as a flagship area; citeturn843414search1
- the composition docs say tools are early and can be inconsistent about inferred/injected interface versions; citeturn735786search0
- Wasmtime already supports `wasmtime run --invoke` for component exports; citeturn215469search1turn215469search2
- `wasm32-wasip3` already exists as a component-producing target, but the rustc book still presents it as transitional; citeturn300361search0
- recent Wasmtime async/component changes and the February 2026 advisory show that runtime posture still matters for review and reproduction. citeturn843414search2turn843414search5

So the missing value is no longer “make components exist.”
The missing value is a **boring component contract bundle** above shifting tooling lineage, versioned WIT boundaries, and composition closure.

## What the crate should provide other people

For maintainers, platform teams, reviewers, and consumers, the crate should provide:

1. **One compact component contract** instead of component truth spread across `Cargo.toml`, WIT files, `wkg` fetches, composition commands, CI YAML, and runtime-specific shell snippets.
2. **A tooling-lineage report** that states whether the artifact came from native targets, a transitional `cargo-component` flow, or explicit post-build composition.
3. **A world-lock report** that keeps package names, world names, interface versions, and mismatch classes explicit.
4. **A composition-closure report** that says whether imports are closed in-bundle, satisfied by the host, or still transitively open.
5. **An exercise receipt** that records whether the component is runnable by `wasi:cli/run`, `--invoke`, or only through a custom host contract.
6. **A diffable component bundle** another person can review or replay without recreating the whole build graph.
7. **A conservative summary** for downstream users explaining what they can run immediately versus what still needs host wiring or manual review.

## Three first-class review objects

### 1. Tooling lineage
This should stay separate from “a `.wasm` file exists.”

Named classes for `0.1`:
- `native_target_build`
- `cargo_component_transitional`
- `native_plus_wac_compose`
- `manual_review_required`

This report should also keep visible:
- target family (`wasm32-wasip2`, `wasm32-wasip3`, or other),
- whether WIT dependencies were resolved through `wkg`,
- whether composition occurred after the initial Rust build,
- and whether runtime posture assumes async/component features beyond a plain build.

### 2. World lock
This should answer questions like:
- what package/world did the component claim?
- which interfaces were imported and exported?
- did the artifact carry explicit versions or rely on inference?
- are there mismatches between an imported interface such as `docs:regex/match` and an exported interface like `docs:regex/match@0.1.0`?

The goal is to stop world/version truth from being reconstructed ad hoc from embedded metadata and failing only during composition.

### 3. Composition closure
This should answer:
- are imports fully satisfied inside the bundle?
- does the component still require host-supplied capabilities or dependencies?
- is the bundle closed enough to hand to another team?
- does it exercise through `wasi:cli/run`, `--invoke`, or only through a custom host profile?

The goal is to stop “it built” from being mistaken for “it is actually runnable in the intended way.”

## Recommended `0.1` command surface

### `cargo component-kit inspect`
Read project facts from `Cargo.toml`, target selection, WIT files, built component artifacts, and optional composition manifests.
Emit early observations without pretending the component is valid yet.

### `cargo component-kit lock`
Normalize package/world/interface information into:
- `world-lock.report.json`
- `interface-index.json`
- `component-summary.md`

### `cargo component-kit check`
Run policy checks for:
- version-inference mismatches,
- imports that remain transitively open,
- target/runtime posture drift,
- unresolved exercise surface,
- and tooling-lineage gaps that still require manual review.

### `cargo component-kit exercise`
Capture one conservative exercise receipt using:
- `wasi:cli/run`,
- `wasmtime run --invoke`,
- or an imported custom-host profile.

This command should capture enough to help another person rerun the component, not attempt to become a full benchmark or observability platform.

### `cargo component-kit diff <old> <new>`
Compare two bundles and classify:
- `tooling_lineage_changed`
- `target_family_changed`
- `world_changed`
- `interface_version_changed`
- `closure_class_changed`
- `exercise_surface_changed`
- `manual_review_boundary_changed`

### `cargo component-kit pack`
Produce one compact `.componentbundle.zip` containing the normalized receipts plus a short summary.

## Recommended crate/workspace split

- `component_kit_model`
  - shared types for lineage, world locks, closure reports, exercise receipts, and diffs
- `component_kit_import`
  - project inspection, WIT import/export parsing, embedded metadata reading
- `component_kit_check`
  - version/closure classification and conservative policy checks
- `component_kit_exercise`
  - Wasmtime-backed exercise receipts and custom-host adapter surface
- `component_kit_pack`
  - summary rendering, diffing, and zip bundle export
- `cargo-component-kit`
  - user-facing cargo subcommand

Optional later adapters:
- `component_kit_cargo_component_import`
- `component_kit_wac_import`
- `component_kit_registry_import`

## `0.1` artifact set

Core artifacts should be:
- `component-kit.toml`
- `tooling-lineage.report.json`
- `world-lock.report.json`
- `composition-closure.report.json`
- `exercise.receipt.json`
- `component-summary.md`
- `componentbundle.zip`

This pass says `0.1` also needs three sharper review artifacts at the center of gravity:
- `tooling-lineage.report.json`
- `world-lock.report.json`
- `composition-closure.report.json`

Those matter because the shipkit gets vague again if it only records “a component exists” without making clear:
- how the component came to exist,
- what exact interface contract it claims,
- and whether it is actually closed/runnable or still relies on outside wiring.

## Discovery order

1. **Project / target inspection**
   - target family
   - crate shape
   - generated component artifacts
2. **Tooling lineage import**
   - native cargo target build
   - `cargo-component` import
   - explicit WAC or other composition steps
3. **World lock normalization**
   - package names
   - worlds
   - imports/exports
   - interface versions
4. **Composition closure classification**
   - closed in bundle
   - host-supplied open imports
   - transitive unresolved imports
5. **Exercise receipt capture**
   - `wasi:cli/run`
   - `--invoke`
   - custom host profile
6. **Bundle + diff**
   - reviewable summary
   - previous-release comparison

## Ranking discipline

The first implementation should not treat “component built successfully” as the verdict.
A good `0.1` should keep separate:
- `component_exists`
- `tooling_lineage_classified`
- `world_lock_captured`
- `composition_closure_classified`
- `exercise_surface_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- native Rust `wasm32-wasip2` / `wasm32-wasip3` component builds
- `cargo-component` transitional workflows
- `wkg` WIT dependency fetching
- WAC composition steps
- Wasmtime exercise surfaces
- rustc target/platform notes for evolving component targets

### Do not flatten into one fake verdict
- “a component file exists”
- “the component has a world”
- “the world versions match”
- “the imports are closed”
- “the component is runnable by generic tooling”
- “the component is safe to hand to another team without host notes”

## Preferred proving grounds

- a plain native `wasm32-wasip2` command component
- a component built through transitional `cargo-component` workflow and then repacked/composed
- a component with explicit imports that still require host-supplied capabilities
- a component pair where version inference mismatch causes failed composition
- a future-facing `wasm32-wasip3` target experiment that should remain visibly transitional

## Non-goals

- not a replacement for Wasmtime
- not a replacement for `cargo-component`, WAC, or `wasm-tools`
- not a universal Wasm package registry client
- not a benchmark/perf platform
- not a promise that every built component is closed and portable automatically

## MVP API sketch

```rust
pub enum ToolingLineageClass {
    NativeTargetBuild,
    CargoComponentTransitional,
    NativePlusWacCompose,
    ManualReviewRequired,
}

pub fn inspect_project(root: &Path) -> Result<ProjectInspection>;
pub fn classify_tooling_lineage(project: &ProjectInspection) -> Result<ToolingLineageReport>;
pub fn lock_worlds(project: &ProjectInspection) -> Result<WorldLockReport>;
pub fn classify_composition_closure(project: &ProjectInspection) -> Result<CompositionClosureReport>;
pub fn write_bundle(bundle: &ComponentBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Track the Rust component-model docs closely as native tooling replaces older recommendations.
- Track WAC/composition ergonomics and keep version inference mismatches explicit.
- Track Wasmtime exercise/runtime changes conservatively, especially around component async behavior.
- Track rustc target evolution for `wasm32-wasip2` / `wasm32-wasip3` without pretending the target story is frozen.
- Preserve `manual_review_required` whenever the crate cannot safely infer closure or exercise posture.
