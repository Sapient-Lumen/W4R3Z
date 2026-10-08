## Current note (rev0399)
Read this kit as the implementation substrate beneath `design/cargo-build-interop-contract-2026Q1.md`.

What changed in rev0399 is not the basic shape of the kit.
What changed is the repo's interpretation:
- **Build Interop Kit** is now promoted as the clearest next **workspace-graph / plan / event / adapter** seam for Cargo in larger build systems;
- **Cargo artifact contract** remains the adjacent **final-output / sidecar / downstream-handoff** seam;
- and future revisions should not flatten discovery, graph, plan, live events, and final artifacts into one fake interoperability layer.

# Design: Build Interop Kit (`cargo interop`, `interop-pack/v0`)

## Goal
Define a stable machine-facing substrate for **workspace discovery, build planning, and execution events** so Cargo can integrate cleanly with IDEs, wrappers, CI, and non-Cargo build systems.

This should not replace Cargo, rust-analyzer, BSP, Bazel/Buck/GN, or Cargo’s existing report work. It should give them a better shared surface.

## References (signals)
- 2026 roadmap: Rust explicitly wants Cargo to integrate into larger build systems and to prototype plumbing commands.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo plumbing goal: current commands are incomplete, `cargo metadata` excludes feature resolution, and `--build-plan` was never a durable answer.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo external-tools docs: current stable surfaces are `cargo metadata`, JSON build messages, and subcommands.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo changelog: `build-plan` was removed in favor of newer directions like plumbing commands, `--unit-graph`, and structured logging.
  https://doc.rust-lang.org/beta/cargo/CHANGELOG.html
- `--unit-graph` already models Cargo’s internal units better than `cargo metadata`, especially for feature resolution and intra-package dependencies.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.94 cycle: structured logging work, `cargo report rebuild`, `cargo report sessions`, and active work on workspace/config discovery.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer discovery/config docs: `workspace.discoverConfig`, JSONL events, `rust-project.json` generation, and `{label}`-aware check commands.
  https://rust-analyzer.github.io/book/configuration
- Fuchsia: real GN-based Rust workflow built around generated `rust-project.json`, with instability caveats.
  https://fuchsia.dev/fuchsia-src/development/languages/rust/editors
- Build Server Protocol: a proven language-agnostic model for IDE ↔ build-tool interop.
  https://build-server-protocol.github.io/docs/specification.html

## Core components

### 1) `workspace-discovery/v0`
An NDJSON stream for discovering a Rust workspace or target context.

Event families:
- `progress`
- `error`
- `finished`

Required ideas:
- canonical workspace root
- originating file or buildfile
- stable workspace identity
- compatibility rule: unknown event kinds must be ignored

This is intentionally close to rust-analyzer’s current discover-command model, but promoted from “provisional editor hook” to versioned contract.

### 2) `workspace-graph/v0`
A versioned description of the Rust workspace as tools need to consume it.

Contents:
- package graph and workspace members
- crate graph / targets / generated-source paths
- toolchain + sysroot identity
- package IDs and optional external build labels
- canonical roots and path-normalization rules
- optional attachment of Cargo-native metadata snapshots

Design rule: do **not** pretend `workspace-graph/v0` is just `cargo metadata` with extra fields. It must be able to express non-Cargo labels and generated-source realities while still mapping cleanly onto Cargo package IDs.

### 3) `build-plan/v0`
A portable “intent” plan for a build.

This is not a promise of exact final shell commands. Build scripts, proc macros, target configuration, and feature resolution can make that impossible to freeze too early.

Instead, `build-plan/v0` should capture:
- units
- edges
- target/profile/toolchain context
- artifact intents
- build-script / proc-macro boundaries
- dynamic-expansion points and reasons

Design rule: use the current `--unit-graph` lessons, not the removed `--build-plan` dream.

### 4) `cargo-events/v0`
An NDJSON execution stream with stable session and unit identity.

Initial event families:
- `session_start` / `session_end`
- `unit_start` / `unit_end`
- `artifact_emitted`
- `build_script_start` / `build_script_end`
- `proc_macro_start` / `proc_macro_end`
- `rebuild_reason`
- `blocked_on_lock` / `waiting_on_unit`
- `diagnostic_ref`

Design rule: this is the live execution/event layer. It complements `--message-format=json` rather than replacing rustc diagnostics.

### 5) `interop-pack/v0`
A bundle format that can carry:
- discovery events
- workspace graph
- build plan
- execution events
- pointers to Cargo report outputs
- raw attachments (`cargo metadata`, `--unit-graph`, rust-analyzer project JSON, BSP payloads)

This is the portable artifact for IDE bug reports, CI analysis, wrapper testing, and cross-tool debugging.

## Reference UX
A reference plugin should expose something like:
- `cargo interop discover`
- `cargo interop export-workspace`
- `cargo interop plan`
- `cargo interop events`
- `cargo interop validate`
- `cargo interop pack`

The plugin should start as an adapter that consumes current Cargo/rust-analyzer surfaces and emits cleaner contracts, not as a giant invasive rewrite.

## BSP bridge
BSP should be treated as an **adapter target**, not the source of truth.

Why:
- BSP is broader than Rust and has useful ideas around targets, compile/test/run/debug.
- Rust still needs its own unit/package/feature/build-script semantics.
- A Rust-specific artifact layer can stay precise while a BSP adapter provides cross-language IDE reuse.

Recommended mapping:
- `workspace-graph/v0` ↔ BSP build targets
- `build-plan/v0` ↔ compile/run/test intent
- `cargo-events/v0` ↔ progress/task notifications
- `interop-pack/v0` ↔ issue/repro attachments outside BSP proper

## What the kit should provide to others
- **IDE authors:** one stable Rust workspace/build surface instead of custom Cargo scraping plus separate non-Cargo special cases.
- **Large monorepo teams:** one contract for Cargo-native and externally orchestrated Rust targets.
- **rust-analyzer and wrappers:** less pressure to expose provisional private-ish formats forever.
- **CI and remote-build tooling:** a graph and event model that is better aligned with what Cargo actually executes.
- **Other archive kits:** a better substrate for cache, perf, replay, report, and policy tooling.

## Hard problems (explicitly scoped)
1. **Dynamic build scripts mean plans are partly discoverable only after execution**
   - v0 must model dynamic expansion honestly instead of hiding it.
2. **Paths are messy**
   - generated files, symlinks, sandbox roots, and per-build output directories must be modeled explicitly.
3. **Cargo-only and non-Cargo labels are both real**
   - preserve Cargo package IDs and allow external labels rather than forcing one naming scheme.
4. **Live event streams and persisted reports are different layers**
   - do not collapse them into one overloaded JSON blob.
5. **Do not make BSP mandatory**
   - it should be a bridge, not a gate.

## Evaluation plan
Pilot on:
1. a normal Cargo workspace with `cargo metadata`, `--message-format=json`, and Cargo report outputs,
2. a workspace with custom build scripts/proc macros,
3. a non-Cargo workspace feeding rust-analyzer via generated project data,
4. a monorepo case where Cargo is wrapped by an outer build system.

Success bar:
- the same repo can be understood by IDEs and CI without bespoke log scraping,
- non-Cargo systems can export Rust workspace/build state without pretending to be Cargo,
- Cargo-native workflows gain a stable machine-facing layer without freezing all internal implementation details,
- and the design composes cleanly with Cargo Report Kit, Workspace Governance Kit, CompileDB Kit, and Resolution Doctor Kit.
