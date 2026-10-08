# Epic Proposal: Reflection Surface Kit (`cargo reflectsurf`)

## One-sentence pitch
Give Rust one reviewable reflection boundary over type-shape metadata, acquisition lanes, value-access capabilities, registry/discovery semantics, and adapter truth so the ecosystem can evolve beyond derive lock-in without disappearing into ad hoc registries and one-off visitor APIs.

## Why this is worthy
This is an ecosystem-shaping contribution because it sits where several important Rust directions are converging:
- Rust is explicitly prototyping compile-time reflection to reduce trait/derive lock-in for serializers, logging stacks, and game-engine tooling.
- Existing libraries already provide serious but incompatible reflection-like surfaces: runtime metadata (`bevy_reflect`), rich shape metadata (`facet`), object-safe structured inspection (`valuable`), version-controlled format extraction (`serde_reflection`), and distributed registration (`inventory`).
- Those libraries are useful today, but they expose different acquisition models, different metadata depth, different mutation semantics, and different registry assumptions.
- If the ecosystem does **not** establish a shared boundary here, compile-time reflection will arrive into a landscape where every downstream tool still invents its own notion of “reflectable”.

## Deliverables
### Schemas / artifact family
- `reflection-subject/v0`
- `reflection-acquisition-profile/v0`
- `reflection-shape-profile/v0`
- `reflection-value-access-profile/v0`
- `reflection-registry-profile/v0`
- `reflection-adapter-profile/v0`
- `reflection-check-report/v0`
- `reflection-diff-report/v0`
- `reflect-pack/v0`

### Reference tooling
- `cargo reflectsurf inventory`
- `cargo reflectsurf shape`
- `cargo reflectsurf access`
- `cargo reflectsurf registry`
- `cargo reflectsurf check`
- `cargo reflectsurf diff`
- `cargo reflectsurf pack`

### Integrations
- `bevy_reflect` adapter
- `valuable` / `tracing` adapter
- `serde_reflection` adapter
- optional `facet` adapter
- registry/discovery adapters (`inventory`, static tables, framework registries)
- future comptime-reflection adapter lane

## Example theory-to-practice scenarios
### 1. “Can arbitrary downstream types participate without adding my derive?”
A serializer, logger, or editor framework wants to document how it obtains type information.
The kit should produce:
- one `reflection-acquisition-profile` saying whether it depends on derives, runtime registries, schema tracing, or comptime reflection,
- one `reflection-shape-profile` describing what metadata it actually consumes,
- and one `reflection-adapter-profile` documenting where that metadata flows.

### 2. Game/editor toolchains with runtime inspection
A crate uses `bevy_reflect`-style metadata and dynamic mutation for editor tooling.
The kit should separate:
- runtime registration semantics,
- dynamic mutation capabilities,
- serialization support,
- and platform/feature caveats for auto-registration.

### 3. Observability and structured logging
A telemetry stack wants nested structured values rather than `Debug` strings.
The kit should show:
- whether only object-safe inspection exists,
- whether mutation or reconstruction is unsupported,
- and whether the adapter is stable, experimental, or feature-gated.

### 4. Migration toward future compile-time reflection
A derive-heavy framework wants to prepare for upstream reflection work.
The kit should record:
- current derive/registry dependence,
- target reflection capabilities,
- blockers and semver/privacy risks,
- and what adapters would become simpler if core reflection lands.

## Distinctness from nearby ideas
This epic is **not**:
- another reflection runtime,
- a schema-only tool,
- a proc-macro migration tool,
- a plugin registry framework,
- or a language RFC for reflection itself.

It is the missing **review boundary** between those things.

## Execution posture
This epic should now be executed as part of the broader **Reflection Transition Stack** with [`design/reflection-transition-stack.md`](../design/reflection-transition-stack.md) and [`design/reflection-transition-pilot-program.md`](../design/reflection-transition-pilot-program.md).

The next credible move is not more vocabulary alone. It is the ranked pilot order: object-safe observability lane → runtime registry/editor lane → compile-time shape/schema lane → derive-heavy migration lane → future core-reflection comparison lane.

## Milestones
### M0 — vocabulary and fixtures
- stabilize minimal v0 schemas
- define acquisition / shape / access / registry taxonomy
- collect representative fixtures:
  - derive-based runtime reflection
  - object-safe inspection only
  - schema-extraction reflection
  - distributed registration
  - partial auto-registration with platform caveats

### M1 — inventory and shape export
- implement subject + acquisition + shape profiles
- support one runtime reflection stack and one schema-extraction stack
- make reflection claims attachable to CI and docs

### M2 — access and registry truth
- implement value-access and registry profiles
- capture ordering/platform caveats honestly
- attach discovery behavior to reflection packs

### M3 — adapters and validation
- add adapter profiles for tracing, schema/codegen, and editor/debug consumers
- emit check reports from smoke tests and round-trip checks

### M4 — migration and future reflection lanes
- add diff reports for shape/access/registry drift
- support migration notes toward future comptime reflection
- attach packs to release / upgrade review

## Non-goals
- Choosing Rust's final reflection design
- Claiming all reflection metadata is stable API
- Flattening runtime mutation, object-safe visiting, and schema extraction into one capability set
- Pretending registry ordering or platform support are irrelevant details
- Replacing `bevy_reflect`, `facet`, `valuable`, `serde_reflection`, or `inventory`

## Why now
- Reflection and comptime goal: https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- Rust 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `bevy_reflect` docs: https://docs.rs/bevy_reflect/latest/bevy_reflect/
- `facet` docs: https://docs.rs/facet/latest/facet/
- `valuable` docs: https://docs.rs/valuable/latest/valuable/
- `tracing` field docs: https://docs.rs/tracing/latest/tracing/field/
- `serde_reflection` docs: https://docs.rs/serde-reflection/latest/serde_reflection/
- `inventory` docs: https://docs.rs/inventory/latest/inventory/

## Strategic outcome
If this succeeds, the ecosystem stops treating reflection as a grab bag of unrelated tricks.
Instead, Rust gets a real review boundary for:
- how reflection data is acquired,
- what shape metadata exists,
- what can be done with reflected values,
- how types are discovered or registered,
- and which adapters are actually supported.

That is the missing substrate needed for future compile-time reflection to compose with today's runtime and schema-oriented ecosystems rather than merely adding a fourth incompatible lane.
