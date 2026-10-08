# Gap: reflection surfaces, type shapes, and registration contracts are still too fragmented

## What is missing
Rust is now explicitly exploring **compile-time reflection**, but the ecosystem still lacks a **portable way to publish reflection truth** across today's existing reflection-like lanes.

Right now there is no standard way to say:
- how a crate acquires reflection information (`derive`, manual impls, runtime registry population, object-safe visitors, format tracing, future comptime reflection),
- what type-shape information is actually exposed (fields, variants, docs, attributes, layout, generics, privacy limits),
- whether reflected values are read-only, mutable, allocatable, serializable, or merely visitable,
- how registries discover types (manual registration, distributed registration, static tables, inventory-style collection),
- what platform/support caveats apply to auto-registration,
- and which adapters are first-class versus opportunistic (debug UI, tracing/logging, schema export, code generation, CLI/config loading, editor tooling).

That gap matters more now because Rust is no longer treating reflection as a fringe wish. The 2025H2 reflection-and-comptime goal proposes a `const fn`-based reflection scheme precisely because new general-purpose crates like serializers, logging systems, and game-engine inspection stacks are hard to roll out when everyone must opt into your traits and derives. The 2026 flagship themes continue that lane under **Constify all the things**, with **prototype reflection** as a named milestone.

So the missing contribution is not just another reflection crate, not just another proc-macro derive, and not just another local type registry.
It is a **reviewable reflection-surface layer** that lets projects publish what reflection information exists, how it is acquired, how dynamic values can be accessed, how registries work, and what evidence backs those claims.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## The current seam is awkward
Rust already has multiple real reflection-like ecosystems, but they do not compose through a shared contract:
- `bevy_reflect` is a general-purpose runtime reflection crate that supports dynamic interaction with values, runtime type metadata, and reflected serialization/deserialization, while noting that missing language features still impose limitations;
- `facet` exposes a `SHAPE` associated const with layout, field, doc-comment, and attribute data, plus runtime manipulation primitives;
- `valuable` provides object-safe value inspection for structured values and is already used as an experimental enrichment path for `tracing` fields;
- `serde_reflection` extracts format descriptions that teams can check into version control and use for cross-language generation;
- `inventory` provides typed distributed registration with no central list, but iteration order is explicitly not guaranteed;
- `bevy_reflect`'s `TypeRegistry` and auto-registration features show that registration/discovery is already a real operational concern, including platform caveats and different backends.

That means the ecosystem is not missing *ways to do reflection-ish work*.
It is missing the **artifact family that records which reflection lane is in play, what metadata or value access it exposes, how registration/discovery happens, and what semantics are intentionally not promised**.

Sources:
- https://docs.rs/bevy_reflect/latest/bevy_reflect/
- https://docs.rs/bevy_reflect/latest/bevy_reflect/struct.TypeRegistry.html
- https://docs.rs/facet/latest/facet/
- https://docs.rs/facet/latest/facet/struct.Shape.html
- https://docs.rs/valuable/latest/valuable/
- https://docs.rs/tracing/latest/tracing/field/
- https://docs.rs/serde-reflection/latest/serde_reflection/
- https://docs.rs/inventory/latest/inventory/
- https://docs.rs/crate/bevy_reflect/0.17.3/source/Cargo.toml.orig

## Why this matters
This gap matters because more and more Rust ecosystem work depends on **type-shape and value-inspection truth** rather than only on trait bounds:
1. **editor/engine/tooling ecosystems** — game engines, inspectors, debuggers, admin UIs, and config editors need to know what type information is available and what can be mutated dynamically;
2. **serialization / schema / interop stacks** — format reflection, code generation, and cross-language tooling need shape truth without assuming one universal derive stack;
3. **observability and diagnostics** — structured logging and telemetry increasingly want nested typed values rather than only `Debug` strings;
4. **plugin and registration systems** — distributed discovery, auto-registration, ordering, and platform support are operationally significant and often implicit today;
5. **future migration planning** — if compile-time reflection lands, teams will need a reviewable way to migrate from derive-heavy or registry-heavy systems without pretending all reflection lanes are interchangeable.

A worthy contribution here is therefore not “reflection for Rust” in the language-design sense.
It is a way to treat **reflection surfaces as reviewable ecosystem infrastructure**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- https://docs.rs/bevy_reflect/latest/bevy_reflect/
- https://docs.rs/facet/latest/facet/
- https://docs.rs/valuable/latest/valuable/
- https://docs.rs/tracing/latest/tracing/field/
- https://docs.rs/serde-reflection/latest/serde_reflection/
- https://docs.rs/inventory/latest/inventory/

## What “good” looks like
A worthy contribution here is **not** one universal runtime reflection crate and not a fake guarantee that all reflection systems expose the same powers.

It is a shared reflection-surface boundary:
- one `reflection-subject/v0` describing the crate / module / type family under review,
- one `reflection-acquisition-profile/v0` describing whether reflection data comes from derives, manual impls, object-safe visitors, schema tracing, registry metadata, or future comptime reflection,
- one `reflection-shape-profile/v0` describing available type metadata (fields, variants, docs, attributes, layout, generics, privacy boundaries, stability caveats),
- one `reflection-value-access-profile/v0` describing read/write/build/traverse/serialize capabilities on reflected values,
- one `reflection-registry-profile/v0` describing discovery, registration, ordering, platform support, and auto-registration posture,
- one `reflection-adapter-profile/v0` describing concrete downstream adapters like tracing, schema/codegen, debug UIs, or config/CLI generation,
- one `reflection-check-report/v0` recording what was actually validated,
- one `reflection-diff-report/v0` describing shape/access/registry drift,
- and one `reflect-pack/v0` bundle for docs, CI, tooling, and migration planning.

That would let Rust teams review reflection claims using explicit artifacts instead of reconstructing them from derive macros, registry setup code, issue threads, platform caveats, and whichever reflection crate happened to be chosen first.

## Non-goals
This gap should not be used to:
- replace language-level reflection design,
- declare one reflection crate as canonical,
- flatten schema extraction, runtime mutation, and logging-oriented visitation into one story,
- or pretend privacy / semver hazards disappear once metadata is exposed.

The job is smaller and sharper:
**make reflection claims legible, composable, and diffable while Rust evolves both compile-time reflection and its existing library-level reflection ecosystems.**
