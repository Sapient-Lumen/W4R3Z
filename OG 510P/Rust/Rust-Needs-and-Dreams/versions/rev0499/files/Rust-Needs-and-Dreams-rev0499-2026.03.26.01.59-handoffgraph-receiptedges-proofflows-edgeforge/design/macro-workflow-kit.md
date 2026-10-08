# Design: Macro Workflow Kit (`cargo macro`, `macro-pack/v0`)

## Goal
Define a portable workflow and artifact contract for Rust macro work so proc-macro inventory, expansion, cost, debugging, and migration planning become reviewable engineering objects instead of scattered local tricks.

This should **not** replace Cargo, rust-analyzer, `cargo-expand`, or the language-level macro roadmap.
It should make those pieces compose better, and make macro-heavy codebases easier to understand and improve.

## References (signals)
- The accepted macro improvements goal explicitly aims to make `macro_rules!` “just as capable as proc macros” for more use cases, with the stated benefits of faster builds, simpler macros, and smaller dependency supply chains.
  https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- The reflection-and-comptime goal explicitly says proc-macro derives have historically been hard to debug and bootstrap from scratch, and positions reflection as a more dynamic/debuggable path for some use cases.
  https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- Cargo now marks proc-macro crates in `cargo tree`, and older Cargo work added `cargo tree -e no-proc-macro`, which are useful visibility primitives but not a complete workflow.
  https://doc.rust-lang.org/beta/releases.html
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- `cargo-expand` is the de facto expansion tool, but it explicitly describes expansion-to-text as a lossy debugging aid.
  https://docs.rs/crate/cargo-expand/latest
- rust-analyzer exposes proc-macro support, ignored macros, and build-script coupling as explicit configuration surfaces.
  https://rust-analyzer.github.io/book/configuration
- Procedural macros still run during compilation, require a dedicated `proc-macro` crate, and share the compiler’s resource/security concerns.
  https://doc.rust-lang.org/reference/procedural-macros.html

## Core components

### 1) `macro-inventory/v0`
Declares what macro-shaped compile-time surface exists in a workspace.

Required ideas:
- proc-macro crate identity and version
- macro kind (`derive`, `attribute`, `function_like`)
- defining crate vs consuming crate edges
- approximate dependency weight (`syn`, `quote`, `proc-macro2`, etc. presence)
- whether the macro is direct, transitive, or re-exported
- optional expansion/cost/debug attachments

This is the inventory layer that Cargo visibility hints toward, but does not yet standardize.

### 2) `macro-expansion-pack/v0`
Portable attachment for targeted expansion snapshots.

Required fields:
- expansion target identity (item / module / test / example)
- tool/backend used
- `raw` vs `pretty` vs `formatted` view markers
- explicit `lossy_text_view: true|false`
- attachment pointers for raw token/JSON output where available
- redaction / truncation metadata
- source hash and feature/target context

Design rule: never pretend textual expansion is exact source truth.
The pack must preserve that `cargo expand`-style views are useful but lossy.

### 3) `macro-cost-report/v0`
Machine-readable macro cost and hotspot report.

Scope:
- proc-macro crate compilation time
- expansion/execution phase attribution where available
- repeated builds across targets/features
- dependency-weight heuristics
- optional “top offenders” summary
- change classification (`new_proc_macro`, `heavier_dependency_stack`, `execution_hotspot`)

The goal is not perfect nanosecond accounting in v0.
The goal is enough signal to prioritize real cleanup work.

### 4) `macro-debug-report/v0`
Structured record of macro failures and debugging context.

Should support:
- macro identity + version
- failing invocation site
- panic vs emitted `compile_error!` vs malformed expansion class
- minimized reproducer pointers
- environment/toolchain context
- IDE/CLI attachment pointers
- known-workaround notes

This becomes the attachable unit for CI, issues, and upstream bug reports.

### 5) `macro-migration-hints/v0`
Explicitly speculative but useful planning artifact.

Should record:
- candidate macro uses that might move to declarative macros as features land
- candidates that are better served by reflection/comptime-style approaches
- migration blockers (unsupported macro_rules feature, runtime reflection not available, ergonomics gap, performance sensitivity)
- expected benefit classes:
  - reduced dependency tree
  - lower compile time
  - easier debugging
  - easier bootstrapping

This is a planning layer, not an auto-refactor promise.

### 6) `macro-pack/v0`
Bundle containing:
- `macro-inventory/v0`
- optional `macro-expansion-pack/v0`
- optional `macro-cost-report/v0`
- optional `macro-debug-report/v0`
- optional `macro-migration-hints/v0`
- raw tool attachments where available

This is the unit that can travel through CI, design review, or issue trackers.

### 7) `cargo macro`
Reference UX:
- `cargo macro inventory`
- `cargo macro expand`
- `cargo macro cost`
- `cargo macro debug`
- `cargo macro migrate`
- `cargo macro pack`

`cargo macro` should begin as an orchestrator / reporter / packer.
It should not try to replace rust-analyzer or own macro expansion internals.

## Shared stack note
Macro Workflow remains part of the broader **Compile-Time Surface Stack**, but it now also forms one pillar of the narrower **Reflection Transition Stack** with [`design/reflection-surface-kit.md`](./reflection-surface-kit.md) and [`design/const-surface-kit.md`](./const-surface-kit.md).

Design rule: **Macro Workflow owns today's proc-macro inventory / expansion / cost / debug / migration truth. It should not silently become the source of truth for runtime reflection semantics or future compile-time reflection capability.**

## What the kit should provide to others
- **Compile-Time Capabilities Kit:** remains the execution-permission and sandboxing layer; Macro Workflow Kit supplies reviewable inventory/cost/debug artifacts above it.
- **Build Cache Kit / Perf Labs:** can consume macro-cost reports as compile-time hotspot evidence.
- **Build Interop Kit:** can attach macro phase events and use `macro-inventory/v0` as a higher-level explanation surface.
- **Observability Kit:** can ingest macro-debug reports without becoming the source of macro-specific truth.
- **Public API Kit / Schema Contract Kit:** can attach expansion/migration notes for derive-heavy public surfaces when relevant.

## Overlap boundaries
- **Not Compile-Time Capabilities Kit:** that kit is about permissions, sandboxing, and deterministic execution policy for build scripts/proc macros. Macro Workflow Kit is about inventory, expansion, debugging, cost, and migration planning.
- **Not Build Cache Kit:** caching explains reuse and misses across builds; this kit explains macro-specific cost and structure.
- **Not Build Interop Kit:** interop standardizes discovery/graph/plan/event surfaces; this kit turns macro-heavy workflows into reviewable artifacts.
- **Not a new macro system:** this does not replace proc macros, `macro_rules!`, or future reflection/comptime work.
- **Not an IDE replacement:** rust-analyzer remains an editor integration surface, not the canonical pack format.

## Hard problems (explicitly scoped)
1. **Expansion views are lossy**
   - Text output is useful but cannot be treated as exact truth.
   - `macro-expansion-pack/v0` must preserve raw/pretty distinctions.

2. **Cost attribution is imperfect**
   - Some macro cost is crate compilation, some is expansion, some is downstream knock-on cost.
   - v0 should favor honest approximations over fake precision.

3. **Migration advice depends on moving language targets**
   - Declarative macro parity and reflection/comptime capabilities are evolving.
   - `macro-migration-hints/v0` must include blockers and confidence levels.

4. **IDE and CLI contexts diverge**
   - rust-analyzer, Cargo, and one-off tools expose different slices of truth.
   - The pack format should normalize metadata and attachments, not force one runtime path.

5. **Macro failures can be sensitive**
   - Expansions and minimized repros may leak internal code structure.
   - Redaction and attachment indirection need to be first-class.

## Minimal adoption path
1. Publish schemas + validators.
2. Ship `cargo macro inventory` and `cargo macro pack` first.
3. Integrate with `cargo-expand`-style output and Cargo tree visibility.
4. Add cost heuristics and debug-report adapters.
5. Add migration hints once declarative/reflection targets become clearer.

## Role in the Compile-Time Surface pilot program
This kit is the **workflow and migration layer** inside [`design/compile-time-surface-pilot-program.md`](./compile-time-surface-pilot-program.md).
It should stay clearly separate from capability policy while still attaching to it. The point is to make proc-macro-heavy workspaces understandable, optimizable, and eventually migratable without pretending authority, debugging, expansion, and future language transitions are one problem.

It should also feed the profile ladder in [`design/compile-time-profile-ladder.md`](./compile-time-profile-ladder.md): some macro-heavy subjects will realistically stop at `narrow-native` or `portable-sandbox`, while others should accumulate enough migration evidence to target `language-first` lanes.
