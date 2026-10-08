# Design: Reflection Surface Kit (`cargo reflectsurf`, `reflect-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **reflection surfaces** in Rust: type-shape metadata, reflection acquisition lanes, value-access capabilities, registry/discovery semantics, and downstream adapter truth.

This should help answer questions like:
- how reflection information for this crate is acquired,
- what type metadata is actually exposed,
- whether reflected values can be visited, mutated, built, serialized, or only inspected,
- how reflected types are registered or discovered,
- what platform or feature-gate caveats apply,
- and which consumers (tracing, schema/codegen, editors, debug UIs, config/CLI generators) can rely on those surfaces.

It should **not** replace language-level reflection design, proc-macro evolution, schema tooling, or any specific reflection runtime.
It should make reflection truth reviewable and attachable.

## References (signals)
- The 2025H2 reflection-and-comptime goal proposes a compile-time-only reflection scheme because general-purpose crates like serializers, logging systems, and game-engine state inspectors are hard to roll out when every ecosystem participant must adopt your traits and derives.
  https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- The same goal says crates like `bevy_reflect` and `facet` would still exist after such a feature, but with different goals and methods of exposing reflection information. That is strong evidence the ecosystem needs a way to compare reflection lanes honestly instead of pretending one future mechanism erases the rest.
  https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- The 2026 flagship themes include **prototype reflection** under **Constify all the things**, showing that reflection is now a named Rust-evolution frontier rather than only an out-of-tree experiment.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `bevy_reflect` is explicitly a general-purpose runtime reflection crate that supports dynamic interaction with values, runtime type metadata, and reflected serialization/deserialization, while warning that missing language features still impose limitations.
  https://docs.rs/bevy_reflect/latest/bevy_reflect/
- `facet` exposes a `SHAPE` associated const with layout, fields, doc comments, attributes, and other metadata, and its `Shape` model includes layout, type ids, generic parameters, docs, and operations for manipulating values at runtime.
  https://docs.rs/facet/latest/facet/
  https://docs.rs/facet/latest/facet/struct.Shape.html
- `valuable` provides object-safe value inspection, and `tracing` already exposes experimental support for `valuable` because its default `Value` model is intentionally minimalist.
  https://docs.rs/valuable/latest/valuable/
  https://docs.rs/tracing/latest/tracing/field/
- `serde_reflection` extracts version-controllable format descriptions and supports cross-language generation and dynamic translation.
  https://docs.rs/serde-reflection/latest/serde_reflection/
- `inventory` provides distributed typed registration with no central list, and explicitly does not guarantee iteration order.
  https://docs.rs/inventory/latest/inventory/
- `bevy_reflect`'s auto-registration features show that registry/discovery backends and platform support are already meaningful configuration surfaces.
  https://docs.rs/bevy_reflect/latest/bevy_reflect/struct.TypeRegistry.html
  https://docs.rs/crate/bevy_reflect/0.17.3/source/Cargo.toml.orig

## Shared stack note
Treat this kit plus [`design/macro-workflow-kit.md`](./macro-workflow-kit.md) and [`design/const-surface-kit.md`](./const-surface-kit.md) as the shared **Reflection Transition Stack**, with [`design/reflection-transition-stack.md`](./reflection-transition-stack.md) and [`design/reflection-transition-pilot-program.md`](./reflection-transition-pilot-program.md) as the synthesis / rollout layer above them.

Design rule: **Reflection Surface owns acquisition / shape / access / registry / adapter truth; Macro Workflow owns current proc-macro burden and migration hints; Const Surface owns compile-time capability/cost/fallback truth.**

## Core components

### 1) `reflection-subject/v0`
Declares the subject whose reflection surface is under review.

Required ideas:
- crate/workspace/module/type-family identity
- feature / target / channel context
- whether the subject is the producer of reflection data, a consumer, or both
- optional links to semantic-context, encoding, compile-time-capabilities, or override artifacts

### 2) `reflection-acquisition-profile/v0`
Describes **how** reflection information is acquired.

Required fields:
- acquisition mode (`derive`, `manual`, `runtime-registry`, `schema-trace`, `object-safe-visit`, `comptime-experiment`, `mixed`)
- source of truth (`impl`, generated metadata, format trace, registry entry, future core reflection API)
- build/runtime dependency posture
- host/target assumptions
- privacy and semver caveats
- unsupported or intentionally omitted metadata

Design rule: do not flatten future compile-time reflection with today's derive- or registry-based lanes.

### 3) `reflection-shape-profile/v0`
Declares what type-shape information is exposed.

Examples:
- fields / tuple slots / enum variants
- names / renamed names / tags / content keys
- docs / attributes / source locations when available
- layout / size / alignment posture
- type parameters / const parameters / variance
- private-field visibility limits
- stability guarantees for identifiers

This is where crates like `facet`, `bevy_reflect`, or future core reflection can differ honestly.

### 4) `reflection-value-access-profile/v0`
Describes what users can do with reflected values.

Examples:
- inspect-only vs mutable access
- field traversal by name/index/path
- dynamic construction or defaulting
- downcasting / typed recovery
- serialization / deserialization support
- visitor-only / object-safe inspection lanes
- allocation / unsafe / invariant caveats

Design rule: never treat “can inspect a value” and “can safely rebuild or mutate it” as the same claim.

### 5) `reflection-registry-profile/v0`
Describes discovery and registration semantics.

Should support:
- explicit/manual registration vs auto-registration
- distributed registration backend (`inventory`, static table, custom loader, none)
- ordering guarantees or lack thereof
- deduplication / replacement / shadowing semantics
- platform support caveats
- feature flags required for registry behavior
- cold-start / load-time / linking assumptions

This is essential because today's reflection ecosystems often hide operational complexity in registration code and feature flags.

### 6) `reflection-adapter-profile/v0`
Declares which downstream adapters are first-class.

Examples:
- tracing / telemetry
- schema / codegen / cross-language export
- editor / inspector / UI generation
- debug / pretty-print / REPL tools
- config / CLI / form generation
- ECS / plugin / app-framework integration

The point is not to promise all adapters, but to make supported ones explicit.

### 7) `reflection-check-report/v0`
Machine-readable validation report.

Can include:
- validated types / registries / adapters
- platforms and features exercised
- shape/access invariants checked
- round-trip or adapter smoke tests
- unsupported or intentionally skipped lanes
- confidence notes and attachment pointers

### 8) `reflection-diff-report/v0`
Explains what changed between two reflection surfaces.

Reason classes may include:
- `shape-expanded`
- `shape-reduced`
- `field-renamed`
- `access-capability-changed`
- `registry-discovery-changed`
- `adapter-added`
- `adapter-removed`
- `platform-caveat-changed`
- `stability-posture-changed`

### 9) `reflect-pack/v0`
Bundle containing:
- `reflection-subject/v0`
- `reflection-acquisition-profile/v0`
- `reflection-shape-profile/v0`
- `reflection-value-access-profile/v0`
- `reflection-registry-profile/v0`
- optional `reflection-adapter-profile/v0`
- optional `reflection-check-report/v0`
- optional `reflection-diff-report/v0`
- raw tool attachments when relevant

### 10) `cargo reflectsurf`
Reference UX:
- `cargo reflectsurf inventory`
- `cargo reflectsurf shape`
- `cargo reflectsurf registry`
- `cargo reflectsurf check`
- `cargo reflectsurf diff`
- `cargo reflectsurf pack`

`cargo reflectsurf` should begin as an orchestrator / reporter / packer.
It should not try to replace any existing reflection runtime.

## What the kit should provide to others
- **Macro Workflow Kit:** records whether derive-heavy systems remain necessary or whether reflection lanes can replace part of them.
- **Const Surface Kit:** can consume comptime-reflection posture without conflating it with general const support.
- **Encoding Surface Kit / Schema Contract Kit:** can attach reflection shape and adapter truth without assuming one universal derive stack.
- **Observability Kit:** can import object-safe inspection capabilities (e.g. `valuable`) without becoming the source of reflection truth.
- **Override Surface Kit / Plugin Surface Kit:** can refer to registry/discovery semantics where reflected types are loaded or registered dynamically.
- **Semantic Context Kit:** remains the compiler-backed semantic graph layer; Reflection Surface Kit records what a particular reflection lane exposes outwardly.

## Overlap boundaries
- **Not Semantic Context Kit:** semantic context is about compiler/Cargo-backed analysis inputs and queries. Reflection Surface Kit is about user-visible metadata and dynamic access surfaces.
- **Not Encoding Surface Kit:** encoding describes wire semantics; reflection describes shape/access/registry surfaces that may feed multiple encodings.
- **Not Macro Workflow Kit:** macro workflow covers proc-macro inventory/cost/debug/migration. Reflection Surface Kit covers the reflection behavior that may replace or complement derives.
- **Not Override Surface Kit:** override surfaces record provider slots and registration semantics broadly; reflection registry profiles focus specifically on type metadata discovery and reflection loading.
- **Not a language feature proposal:** this kit does not choose the design of Rust reflection.

## Hard problems (explicitly scoped)
1. **Different reflection lanes expose different truths**
   - schema extraction, runtime mutation, and object-safe visitation are not interchangeable.
   - v0 must preserve incompleteness and asymmetry.

2. **Registration semantics are operationally messy**
   - ordering, platform support, and linker/runtime initialization vary.
   - the registry profile must keep those caveats explicit.

3. **Privacy and semver hazards are real**
   - reflection can surface names, docs, layout, or field structure.
   - the kit must distinguish stable promises from opportunistic observations.

4. **Compile-time reflection may land before the ecosystem converges**
   - v0 must support future comptime lanes without pretending they collapse today's libraries into one model.

5. **Adapters tempt overclaiming**
   - a crate might support tracing-oriented visitation but not safe dynamic mutation.
   - adapter truth needs to be specific and bounded.

## Minimal adoption path
1. Publish schemas + validators.
2. Ship `cargo reflectsurf inventory` and `cargo reflectsurf pack` first.
3. Add adapters for `bevy_reflect`, `valuable`, `serde_reflection`, and one registry backend.
4. Add diffing and check reports.
5. Add comptime-reflection lanes once upstream experiments are usable.
