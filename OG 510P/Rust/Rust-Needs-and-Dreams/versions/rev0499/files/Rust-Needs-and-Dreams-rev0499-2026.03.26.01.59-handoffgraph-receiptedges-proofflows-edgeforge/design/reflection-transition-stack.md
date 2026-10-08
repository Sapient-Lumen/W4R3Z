# Design: Reflection Transition Stack

## Goal
Treat Rust's emerging reflection frontier as a **transition problem**, not as a single-tool winner.

This stack makes three things compose without flattening them:
- today's **macro-heavy acquisition lanes**,
- today's **runtime / object-safe / schema-tracing reflection lanes**,
- and tomorrow's **compile-time reflection / const-introspection lanes**.

The missing contribution is not another reflection runtime, derive helper, or registry macro.
It is a portable review boundary that lets the ecosystem say:
- how type information is acquired today,
- what metadata and value access actually exist,
- which proc-macro, orphan-rule, and registry burdens are still being paid,
- which downstream adapters (telemetry, schema/codegen, editors, config/CLI generation, debug UIs, scripting) really work,
- and what migration path exists toward future language-supported reflection.

## Why this stack now
Rust's current signals are unusually aligned here:
- Rust's 2026 flagship themes explicitly include **prototype reflection** under **Constify all the things**, which means reflection is now an active language frontier rather than only an ecosystem curiosity.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H2 reflection-and-comptime goal proposes a `const fn`-based compile-time reflection scheme, explicitly says proc-macro derives have historically been hard to debug and bootstrap, and says crates like `bevy_reflect` and `facet` would still exist afterwards but with different goals.
  https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- The 2025H1 macro-improvements goal argues that replacing many proc-macro use cases with declarative macros can improve build times, simplify macros, and reduce dependency chains.
  https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- The 2025 compiler-performance survey says stabilizing language features could remove some build scripts or proc macros and speed up compilation across the ecosystem.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The August 2025 program-management update says Bevy and gamedev users raised reflection as a major pain point, describes `derive(Reflect)` workflows as difficult to write/debug, and explains why the orphan rule keeps many useful types outside easy reflection coverage.
  https://blog.rust-lang.org/inside-rust/2025/09/11/program-management-update-2025-08/
- The ecosystem already spans several legitimate but incompatible lanes:
  - `bevy_reflect` for general-purpose runtime reflection, dynamic interaction, and runtime registration,
  - `facet` for rich shape metadata via an associated const,
  - `valuable` for object-safe inspection with `tracing` integration,
  - `serde_reflection` for version-controlled format extraction,
  - and proc-macro workflows that still dominate derive-heavy ecosystems.
  https://docs.rs/bevy_reflect/latest/bevy_reflect/
  https://docs.rs/facet/latest/facet/
  https://docs.rs/valuable/latest/valuable/
  https://docs.rs/tracing/latest/tracing/field/index.html
  https://docs.rs/serde-reflection/latest/serde_reflection/

## Stack members and boundaries
### 1) Macro Workflow Kit
Owns **today's acquisition and migration burden**:
- proc-macro inventory,
- expansion/debug/cost evidence,
- current derive/attribute/function-like posture,
- orphan-rule or wrapper pressure where relevant,
- migration hints toward declarative or reflection-based alternatives.

Macro Workflow should remain the source of truth for **what compile-time machinery is still being paid for today**.

### 2) Reflection Surface Kit
Owns **the outward reflection contract**:
- acquisition mode,
- shape metadata depth,
- value-access posture,
- registry/discovery semantics,
- adapter truth.

Reflection Surface should remain the source of truth for **what introspection a consumer can actually rely on**.

### 3) Const Surface Kit
Owns **compile-time execution posture**:
- which reflection/introspection lanes are const-only,
- channel/MSRV sensitivity,
- evaluator-cost and code-size posture,
- runtime fallback and migration notes.

Const Surface should remain the source of truth for **what future compile-time reflection lanes really cost and where they are usable**.

## Shared design rule
Treat these as one **Reflection Transition Stack**, but keep their truths separate:
- **Macro truth** is not reflection truth.
- **Runtime reflection** is not compile-time reflection.
- **Visit-only inspection** is not mutation or reconstruction.
- **Schema extraction** is not a universal reflection model.
- **Registry/discovery behavior** is not type-shape stability.
- **Future core reflection** should import and compare existing lanes, not erase them by declaration.

## What an epic contribution would look like
The proposal-layer candidate is now [`proposals/epic-reflection-transition-stack.md`](../proposals/epic-reflection-transition-stack.md): a thin `cargo reflect-transition` / `reflection-transition-pack/v0` layer above Macro Workflow + Reflection Surface + Const Surface rather than a new runtime reflection winner or a premature language-level universal manifest.

A worthy contribution here would not be:
- another runtime reflection crate,
- another derive helper,
- another registry framework,
- or a premature “universal reflect trait”.

It would be:
1. a shared vocabulary for reflection lanes,
2. portable reports and packs that compare those lanes honestly,
3. migration artifacts that let macro-heavy ecosystems plan transitions,
4. adapter profiles that make downstream consumers explicit,
5. and ranked pilots proving where reflection is already good enough, where it is inspect-only, where it is schema-shaped, and where the ecosystem should still wait.

## Core artifact handoff
This stack should treat the following existing artifacts as the execution substrate:
- `macro-inventory/v0`, `macro-cost-report/v0`, `macro-debug-report/v0`, `macro-migration-hints/v0`
- `reflection-acquisition-profile/v0`, `reflection-shape-profile/v0`, `reflection-value-access-profile/v0`, `reflection-registry-profile/v0`, `reflection-adapter-profile/v0`
- `const-capability-profile/v0`, `const-parameter-profile/v0`, `const-eval-cost-profile/v0`, `const-fallback-profile/v0`

A later cross-stack bundle can stay minimal and explicit:
- `reflection-transition-pack/v0`
  - one macro pack,
  - one reflect pack,
  - one const pack,
  - optional consumer-import notes,
  - explicit lossiness / unsupported-lane notes.
- companion renderings should stay thin and consumer-specific via `reflection-transition-handoff/v0` rather than pretending one report works equally well for observability, editor/config, schema/codegen, maintenance, and assistant consumers.

## Ranked next move
The next credible execution step is the ranked rollout in [`design/reflection-transition-pilot-program.md`](./reflection-transition-pilot-program.md), which should start with structured-observability and runtime-registry lanes, then compare shape/schema lanes, then tackle derive-heavy migration planning, and only after that widen to future core-reflection consumers.

## Distinctness from nearby stacks
- **Compile-Time Surface Stack** remains about authority, determinism, and replacement/governance of compile-time execution broadly.
- **Reflection Transition Stack** is narrower: it is about how introspection ecosystems compare and migrate.
- **Encoding Surface Kit / Schema Contract Kit** remain downstream consumers of reflection shape/access truth, not the source of it.
- **Semantic Context Kit** remains compiler-backed semantic analysis, not runtime or library reflection.
- **Plugin / Override / Config surfaces** may import registry/discovery facts, but they do not define reflection semantics.

## Strategic outcome
If this succeeds, Rust gets a way to evolve from today's derive-heavy and runtime-reflection ecosystems toward future compile-time reflection **without pretending the transition is automatic or that one lane should silently replace the others**.
