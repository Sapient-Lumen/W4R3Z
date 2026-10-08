# Epic: Build Interop Kit (`cargo interop`, workspace/build/event contracts)

## Summary
Promote Cargo’s emerging plumbing direction into a coherent ecosystem substrate for **workspace discovery, graph export, build intent, and execution events**:
- `workspace-discovery/v0`
- `workspace-graph/v0`
- `build-plan/v0`
- `cargo-events/v0`
- `interop-pack/v0`

Then ship a reference plugin that bridges current Cargo surfaces, rust-analyzer discovery, and optional BSP adapters.

## Why now
- Rust’s 2026 roadmap explicitly says the project wants Cargo to integrate into larger build systems and to prototype plumbing commands.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The accepted Cargo plumbing goal already laid out the stages of a build Cargo may need machine-facing commands for: locating the project, reading manifests and lockfiles, resolving features, planning the build, executing it, and staging artifacts.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo 1.94 shows the right direction but also the incompleteness of the current boundary: structured logging work is underway, `cargo report rebuild` and `cargo report sessions` exist, and workspace/configuration discovery still has sharp edges.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer and real non-Cargo environments are already using provisional discovery/event conventions and generated `rust-project.json`; this is useful evidence of demand, but not yet a durable shared contract.
  https://rust-analyzer.github.io/book/configuration
  https://fuchsia.dev/fuchsia-src/development/languages/rust/editors


## Relationship to adjacent frontier work
This epic is **not** the same thing as the Cargo artifact contract.

Keep the seams separate:
- **Build Interop Kit** = discovery, workspace/unit graph, build intent, execution events, adapter handoffs.
- **Cargo artifact contract** = final-output identity, origin/staging semantics, sidecars, downstream artifact handoffs.

The archive needs both.
One keeps outer build systems, editors, and wrappers from inventing bespoke workspace/graph glue.
The other keeps release/inventory/repro/support consumers from rebuilding final-artifact truth from scratch.

## Deliverables

### D1 — Contracts + fixtures
- schemas/examples for `workspace-discovery/v0`, `workspace-graph/v0`, `build-plan/v0`, `cargo-events/v0`
- compatibility rules and golden fixtures
- canonicalization/redaction guidance

### D2 — Reference adapter
- `cargo interop export-workspace`
- `cargo interop plan`
- `cargo interop events`
- `cargo interop validate`
- `cargo interop pack`

This adapter should consume current Cargo/rust-analyzer surfaces first instead of requiring immediate upstream stabilization.

### D3 — BSP bridge
- optional adapter that maps `workspace-graph/v0` and `build-plan/v0` into BSP concepts
- enough compile/test/run/progress support to prove cross-IDE reuse

### D4 — Archive integration points
- Cargo Report Kit consumes `cargo-events/v0` session IDs and attaches report references.
- Workspace Governance Kit consumes `workspace-graph/v0` for inheritance/explain tooling.
- CompileDB Kit attaches native compile graph information when build scripts emit C/C++ compilations.
- Resolution Doctor Kit and Feature Kit attach resolved-unit/feature provenance.

## Milestones
### M0 — Narrow the schemas
- keep v0 minimal
- prefer pointers/attachments over giant monolithic documents
- define identity and canonical path rules early

### M1 — Make Cargo-native workflows better first
- export from normal Cargo workspaces
- correlate `cargo metadata`, `--unit-graph`, and `--message-format=json`
- attach Cargo report session references where available

### M2 — Make non-Cargo discovery less bespoke
- rust-analyzer-compatible discovery stream
- generated-source and build-label support
- prove the model against one GN/Buck/Bazel-style example

### M3 — Bridge outward
- BSP adapter
- IDE fixture tests
- reproducible `interop-pack/v0` bug attachments

## Success criteria
- A Rust workspace can be described once and reused across IDEs, CI, and wrappers.
- Cargo and non-Cargo systems can share a stable Rust graph/event vocabulary without pretending to share the same outer build tool.
- Tool authors stop choosing between underspecified `rust-project.json`, unstable `--unit-graph`, and brittle text scraping.
- The new layer complements — not duplicates — Cargo Report Kit and Workspace Governance Kit.

## Risks / mitigations
- **Over-scope risk:** keep v0 focused on discovery/graph/plan/events and use attachments for everything else.
- **Cargo internals drift:** start as an adapter around existing public-ish outputs, then upstream only proven pieces.
- **BSP mismatch:** treat BSP as an adapter target, not the canonical schema.
- **Path/privacy problems:** build in redaction and canonicalization rules from the start.
