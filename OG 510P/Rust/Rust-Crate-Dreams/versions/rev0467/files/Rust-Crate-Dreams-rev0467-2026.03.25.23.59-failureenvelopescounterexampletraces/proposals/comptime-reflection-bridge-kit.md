---
id: P-0439
title: Comptime Reflection Bridge Kit — schema-source receipts, coverage-scope reports, and execution-posture truth across runtime reflection, static shape exports, and future const reflection
status: idea
domains: [language, reflection, metaprogramming, codegen, serialization, devtools]
last_reviewed: 2026-03-21
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
  - https://docs.rs/bevy/latest/bevy/reflect/index.html
  - https://docs.rs/bevy/latest/bevy/reflect/struct.TypeRegistry.html
  - https://docs.rs/crate/facet/latest
  - https://docs.rs/facet-reflect/latest/facet_reflect/
  - https://docs.rs/serde-reflection/latest/serde_reflection/
---

# Problem

Rust is actively exploring a compile-time reflection model based on `const fn`, while today’s ecosystem already has several materially different reflection-like sources.

That makes the missing layer sharper, not blurrier:

- the Rust project goal is explicitly about **compile-time-only** const-eval values for now,
- `bevy_reflect` uses derives and a runtime `TypeRegistry`, with generic monomorphizations still requiring explicit registration,
- `facet` exposes static `SHAPE` metadata and `facet-reflect` adds runtime value views on top of that shape model,
- and `serde_reflection` can extract useful format descriptions without claiming to be a full general-purpose reflection system.

The missing crate is therefore not “Rust reflection, solved once and for all”.
It is a **bridge** that gives other people a compact, portable schema artifact and a realistic migration path across three worlds:

1. today’s runtime registries and derive-based reflection,
2. today’s static shape exports and neighboring schema projections,
3. tomorrow’s experimental compile-time reflection adapters.

# What it provides

- `type-schema.json` — a narrow, portable schema IR for structs, enums, fields, selected annotations, and comparison-safe identity.
- `schema-source.receipt.json` — records which source family produced the export and what authority class it has.
- `coverage-scope.report.json` — records whether the export covers declared type families, observed concrete instantiations, or only a projection such as serialization format structure.
- `execution-posture.receipt.json` — records whether the consumer needs runtime registry state, static generated tables, or compile-time-only adapter output.
- `loss-accounting.report.json` — records what metadata was preserved, dropped, synthesized, or still manual-review-only.
- `reflect.diff.json` — structural changes between two schema views.
- `bridge-manifest.toml` — declares adapters, metadata-class priorities, and authority rules.
- `cargo reflect-bridge export` — emits schema artifacts from one crate/workspace/source.
- `cargo reflect-bridge compare` — compares two exports and explains lost or newly available information.

# What the crate should provide other people

1. **A shared schema artifact** that can outlive any one reflection crate.
2. **A source-authority receipt** so teams can tell whether an export came from a runtime registry, an associated const, a format projection, or a future compile-time adapter.
3. **A coverage-scope report** so registered monomorphizations do not masquerade as generic-family coverage.
4. **An execution-posture receipt** so compile-time-only metadata and runtime mutation-capable reflection stop collapsing into one fake “reflection support” claim.
5. **A loss-accounting report** so bridge adapters stay honest about dropped docs, attributes, bounds, value operations, or synthesized metadata.
6. **A migration bridge** from derive-heavy/runtime-heavy systems to future compile-time reflection experiments.

# Persona / who it’s for

- framework authors with reflection-like metadata needs
- tool authors building schema/CLI/editor/generation pipelines
- serialization or migration tool maintainers
- early adopters of future reflection/comptime experiments

# Users & user stories

- **Framework author**: “I need field/type metadata, but I don’t want to hard-couple my whole toolchain to one reflection crate forever.”
- **Tool author**: “Export a single schema IR from several reflection sources and diff it in CI.”
- **Migrating project**: “Compare our Bevy registry export with a future compile-time adapter and see what changed.”
- **Library maintainer**: “Generate static metadata tables without forcing a runtime registry into my binary.”
- **Reviewer**: “Tell me whether this export covers generic families, concrete instantiations only, or just a serialization-format projection.”

# Prior art (and why it’s insufficient)

- `bevy_reflect` is a powerful, general-purpose runtime reflection system, but it is intentionally shaped around its own registry, derives, and dynamic operations.
- `facet` / `facet-reflect` show a different design with static shape metadata plus runtime value views.
- `serde_reflection` extracts format descriptions that are useful for compatibility and code generation, but that authority class is narrower than full type-shape reflection.
- The Rust project’s reflection/comptime experiment is about a future language mechanism, not about a shared migration artifact for ecosystem tools today.

What remains missing is a **schema-source + coverage-scope + execution-posture + loss-accounting** layer that lets multiple reflection strategies meet in one place without being flattened into one fake capability story.

# Design goals

1. **Bridge, don’t canonize** — do not pretend one ecosystem model is the single truth.
2. **Schema first** — exported artifacts should be portable and diffable.
3. **Authority aware** — source family and authority class must stay explicit.
4. **Coverage honest** — generic-family support, registered subsets, and format-only projections must not collapse together.
5. **Execution-posture aware** — static tables, runtime registries, and compile-time-only adapters are different product surfaces.
6. **Loss-accounting first** — adapters should record what was dropped or synthesized.
7. **Future-compatible** — a future const-reflection adapter should fit naturally into the same artifact story without pretending the language design is already settled.

# MVP surface

- Minimal types: `TypeSchema`, `SchemaSourceReceipt`, `CoverageScopeReport`, `ExecutionPostureReceipt`, `LossAccountingReport`, `BridgeManifest`, `SchemaDiff`
- Minimal functions:
  - `export_schema()`
  - `observe_source()`
  - `report_coverage_scope()`
  - `report_execution_posture()`
  - `report_losses()`
  - `compare_schema()`
- Feature flags:
  - `bevy`
  - `facet`
  - `serde-reflection`
  - `macro-export`
  - `rustdoc`

# Compatibility story

- Works with today’s derive/runtime systems first.
- Keeps future const-reflection support as an adapter, not an assumption.
- Lets tools pin which metadata categories and authority classes they require.
- Should degrade honestly when a source ecosystem cannot represent some metadata.
- Keeps runtime mutation capability adjacent rather than silently on-surface for every export.

# Conformance & fixtures

- Fixtures for named/tuple/unit structs, enums, generics, doc comments, selected annotations, skipped fields, and opaque types.
- Goldens for adapter loss accounting: “generic family downgraded to registered subset”, “format projection only”, “runtime mutation omitted”, and “annotation synthesized.”
- Cross-export comparisons between runtime registries, static shape exports, and future compile-time adapter sketches.
- Corpus of schema diffs used by downstream tools (CLI/schema/config/editor) to validate stability.

# Path to boring stability

- Stabilize `type-schema.json`, `schema-source.receipt.json`, and `coverage-scope.report.json` before adding lots of rich metadata.
- Keep the schema core intentionally narrower than any one reflection framework.
- Treat adapter loss reports as part of the normal UX.
- Add future comptime adapters only when the language experiment is concrete enough to be useful.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A crate that exports a compact type-schema IR from one reflection-like source, emits source/coverage/execution/loss receipts, and compares two schema exports with explicit claim ceilings.

# De-risk plan

1. Start with structs/enums/fields/docs/selected annotations only.
2. Keep runtime adapters, static shape export, and future compile-time adapters as separate modules.
3. Avoid baking in final language-level reflection assumptions.
4. Prove usefulness first on one or two downstream tool categories, such as config/schema generation and CLI metadata.

# Non-goals

- Not a final Rust reflection standard.
- Not a replacement for `bevy_reflect`, `facet`, or `facet-reflect`.
- Not a replacement for `serde_reflection`.
- Not a macro system overhaul.
- Not a promise that future const reflection will expose exactly this schema.
- Not a claim that every export supports runtime mutation or registry-free execution.

# Architecture & API sketch

```rust
pub struct SchemaSourceReceipt {
    pub source_family: SourceFamily,
    pub capture_mode: CaptureMode,
    pub authority_class: AuthorityClass,
    pub registry_population_basis: RegistryPopulationBasis,
}

pub struct ExecutionPostureReceipt {
    pub build_time_export: BuildTimeExport,
    pub runtime_dependency: RuntimeDependency,
    pub mutation_surface: MutationSurface,
    pub portability_class: PortabilityClass,
}

pub fn export_schema(input: &BridgeInput, manifest: &BridgeManifest) -> Result<TypeSchema>;
pub fn observe_source(input: &BridgeInput) -> Result<SchemaSourceReceipt>;
pub fn report_execution_posture(input: &BridgeInput) -> Result<ExecutionPostureReceipt>;
pub fn compare_schema(old: &TypeSchema, new: &TypeSchema) -> SchemaDiff;
```

Bundle draft: `bridge-manifest.toml`, `type-schema.json`, `schema-source.receipt.json`, `coverage-scope.report.json`, `execution-posture.receipt.json`, `loss-accounting.report.json`, `reflect.diff.json`, `notes.md`.

# Security / safety model

- No hidden code execution beyond the compile/build step already needed for metadata generation.
- Support redaction of doc strings or selected annotations in exported bundles.
- Make synthesized or lossy metadata explicit.
- Keep generated-table formats deterministic and versioned.

# Maintenance & governance plan

- Version the schema core carefully and slowly.
- Keep adapters out-of-core where practical.
- Maintain a cross-ecosystem fixture corpus.
- Publish a compatibility matrix showing which metadata classes and execution postures each adapter can provide.

# Milestones

## 0.1
- schema IR
- one runtime or static adapter
- source / coverage / execution / loss receipts
- schema diff + summary

## 0.2
- second adapter
- generated metadata table export
- mixed-source comparison and loss taxonomy

## 1.0
- stable schema core
- cross-ecosystem migration guidance
- CI/report adapters

# Open questions

- What is the smallest schema core that is still broadly useful?
- Which metadata categories should be first-class versus optional annotations?
- How should future const-reflection outputs be recorded if they expose compile-time-only information unavailable at runtime?
- What is the narrowest honest way to compare static shape exports against registry snapshots?

# Sources

- Reflection and comptime goal: https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- `bevy::reflect` docs: https://docs.rs/bevy/latest/bevy/reflect/index.html
- `TypeRegistry`: https://docs.rs/bevy/latest/bevy/reflect/struct.TypeRegistry.html
- `facet`: https://docs.rs/crate/facet/latest
- `facet-reflect`: https://docs.rs/facet-reflect/latest/facet_reflect/
- `serde_reflection`: https://docs.rs/serde-reflection/latest/serde_reflection/
