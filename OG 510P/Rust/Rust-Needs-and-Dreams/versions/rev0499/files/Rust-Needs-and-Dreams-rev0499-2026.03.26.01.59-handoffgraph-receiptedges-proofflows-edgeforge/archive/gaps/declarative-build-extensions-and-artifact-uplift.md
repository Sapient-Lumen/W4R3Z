# Gap: Declarative build extensions and final-artifact export are still fragmented

## Summary
Rust still relies on `build.rs` as a powerful escape hatch, but the ecosystem now has enough upstream motion to see a cleaner missing seam.

What is missing is not merely “a better build script helper crate”. The missing contribution is a **versioned build-extension contract** that can:
- replace a meaningful share of ad hoc `build.rs` wrappers with structured configuration,
- make parameter passing and multi-step build behavior auditable,
- preserve `OUT_DIR` isolation while still allowing **selected** final artifacts to be uplifted safely into Cargo’s final artifact surface, and
- emit machine-readable reports that compose with sandboxing, caching, and build interop.

## Why now
- Cargo now has an explicit roadmap issue to **reduce the need for users to write build scripts**, arguing that doing so would improve build times, reduce bugs, and shrink the dependency-review audit scope.
  https://github.com/rust-lang/cargo/issues/14948
- Cargo still documents **metabuild** as the unstable declarative-build-script path, and the tracking issue now clearly names the remaining seams: multiple build scripts, parameter passing, build-script delegation, and conflict semantics.
  https://doc.rust-lang.org/beta/cargo/reference/unstable.html
  https://github.com/rust-lang/cargo/issues/14903
- Cargo’s 1.93 development-cycle update shows an active design path for **custom final artifacts** created by build scripts, centered on explicit directives, collision checking, selected-package uplift, and Cargo-managed locking rather than direct write access to `artifact-dir`.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Rust’s sandboxed build-scripts goal makes the architectural direction even clearer: build scripts should become more deterministic, less overpowered, and easier to reason about for caching and security.
  https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html

## What exists already
- RFC 2196 gives Rust a declared path for **declarative build scripts** sourced from dependencies rather than bespoke per-crate wrapper logic.
  https://rust-lang.github.io/rfcs/2196-metabuild.html
- Cargo’s build-script model already has a few structured seams: `links`, `cargo::metadata`, rerun directives, and `OUT_DIR` isolation.
  https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo’s build-systems RFC explicitly identified **declarative native dependencies** as a long-term goal, because bespoke build scripts around `pkg-config` / compiler probes are difficult and error-prone.
  https://rust-lang.github.io/rfcs/2136-build-systems.html

## What is still missing
The missing seam is a **shared contract layer**:
- a canonical manifest for declarative build extensions,
- a structured parameter channel,
- explicit conflict and ordering semantics for multi-step build behavior,
- a safe final-artifact export description rooted in `OUT_DIR` rather than target-dir spelunking,
- and reviewable reports that other kits can consume.

Without that layer, Cargo still has to choose between two bad extremes:
- opaque, arbitrary `build.rs` behavior, or
- narrow one-off upstream fixes that solve one build-script use case at a time without converging the model.

## Candidate contribution
Promote a **Build Extension Kit** with:
1. `build-ext-manifest/v0` for declarative build steps, parameters, and declared inputs,
2. `build-ext-report/v0` for resolved steps, observed inputs, timings, and generated outputs,
3. `build-artifact-export/v0` for safe artifact uplift requests rooted in `OUT_DIR`,
4. `build-artifact-report/v0` for copies, collisions, and selected-package decisions,
5. `build-ext-pack/v0` as the portable bundle.

## Overlap boundaries
- **Not Compile-Time Capabilities Kit:** that kit governs permissions and sandbox policy for arbitrary execution. This kit tries to reduce how much arbitrary execution is needed in the first place.
- **Not Build Interop Kit:** that kit exports workspace/build discovery, graphs, plans, and events. This kit standardizes the build-extension behavior that such plans/events need to model.
- **Not FFI Boundary Kit:** FFI kits care about external interface contracts; this kit cares about the build-time machinery that might generate or stage those interfaces.
