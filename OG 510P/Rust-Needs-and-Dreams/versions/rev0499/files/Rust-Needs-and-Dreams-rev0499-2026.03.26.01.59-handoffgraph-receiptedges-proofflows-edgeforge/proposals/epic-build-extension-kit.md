# Epic: Build Extension Kit (`cargo buildext`, `build-ext-pack/v0`)

## Goal
Turn the best current ideas around metabuild, parameter passing, delegated build steps, and safe final-artifact export into one portable, auditable contract layer.

## Why this is ecosystem-worthy
- **Security / auditability:** fewer opaque `build.rs` escape hatches and clearer review surfaces when imperative steps remain.
- **Performance / caching:** declared inputs and ordered steps are easier to cache and reason about than ad hoc script behavior.
- **Interop:** external tools and larger build systems can model build extensions without target-dir archaeology.
- **UX:** generated shell completions, templates, manifests, and similar outputs become first-class rather than hidden in `OUT_DIR` hacks.

## Deliverables
1. `build-ext-manifest/v0`
2. `build-ext-report/v0`
3. `build-artifact-export/v0`
4. `build-artifact-report/v0`
5. `build-ext-pack/v0`
6. A reference `cargo buildext` prototype that validates manifests, runs adapters over current Cargo behavior, and emits portable reports.
7. A migration guide for common build-script patterns:
   - metadata-driven code generation,
   - shell completions / man pages,
   - straightforward native-library probe + link cases,
   - generated binding / config files that should remain inside Cargo-managed boundaries.

## Milestones
### M1 — schemas + fixtures
- Define the v0 manifest/report/export/report schemas.
- Create fixtures covering success, conflict, and fallback-imperative cases.

### M2 — adapter prototype
- Build a prototype that consumes current `Cargo.toml` metadata and build-script outputs.
- Emit `build-ext-report/v0` and `build-artifact-report/v0` from real builds.

### M3 — conflict semantics + package-selection rules
- Nail down step ordering, conflicting metadata/link directives, and selected-package artifact uplift.
- Make “why was this export rejected?” easy to answer.

### M4 — sandbox / policy / cache integration
- Feed reports into Compile-Time Capabilities Kit and cache/report tooling.
- Demonstrate that declared inputs/outputs improve determinism and reviewability.

### M5 — upstream path
- Distill the smallest credible pieces for upstream Cargo experimentation rather than demanding one giant stabilization event.

## Non-goals
- Replacing all `build.rs` logic.
- Solving every native dependency or cross-compilation problem in v0.
- Turning Cargo into a general-purpose build language.

## Why now
Cargo already has the ingredients, but not the contract:
- the roadmap issue to reduce build scripts,
- the existing metabuild lane,
- active work on multiple build scripts / delegation / parameter passing,
- and a concrete Cargo-managed design discussion for final-artifact uplift.

That is exactly the moment when this archive should prioritize a **shared artifact boundary** instead of another wrapper crate.

## References
- https://github.com/rust-lang/cargo/issues/14948
- https://github.com/rust-lang/cargo/issues/14903
- https://rust-lang.github.io/rfcs/2196-metabuild.html
- https://doc.rust-lang.org/beta/cargo/reference/unstable.html
- https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://rust-lang.github.io/rfcs/2136-build-systems.html
- https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html

## Relationship to the Compile-Time Surface stack
This proposal is the **structured replacement pillar** of the broader compile-time stack described in [`design/compile-time-surface-pilot-program.md`](../design/compile-time-surface-pilot-program.md).
Its success should be measured partly by how many common imperative build patterns become declarative and reviewable, not only by how elegantly imperative paths are documented.
