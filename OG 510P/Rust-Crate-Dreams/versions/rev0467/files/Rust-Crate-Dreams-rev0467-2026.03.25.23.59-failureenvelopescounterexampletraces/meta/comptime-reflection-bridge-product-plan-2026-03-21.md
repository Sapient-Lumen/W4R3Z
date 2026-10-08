# Comptime Reflection Bridge Kit — product plan (2026-03-21)

This note sharpens **P-0439 Comptime Reflection Bridge Kit** into an implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0439** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to standardize all of Rust reflection, replace runtime reflection crates, or guess the final shape of language-level comptime reflection.
It should provide one boring, reviewable bridge layer above today's mixed reflection substrate.

`0.1` should make four things first-class:

1. **schema source** — where the exported shape came from and what authority class it has;
2. **coverage scope** — whether the export covers declared families, observed monomorphizations, or only a projection such as serialization format structure;
3. **execution posture** — whether the consumer needs runtime registry state, static generated tables, or compile-time-only adapters;
4. **loss accounting** — what metadata was preserved, dropped, synthesized, or still manual-review-only while bridging across sources.

## What `0.1` should provide other people

- one compact `schema-source.receipt.json`
- one compact `coverage-scope.report.json`
- one compact `execution-posture.receipt.json`
- one compact `loss-accounting.report.json`
- one compact `type-schema.json`
- one rendered `reflection-bridge.summary.md`
- one diff command for release reviewers and tool authors

## Commands worth shipping first

- `cargo reflect-bridge init`
- `cargo reflect-bridge export`
- `cargo reflect-bridge check`
- `cargo reflect-bridge compare <old> <new>`
- `cargo reflect-bridge summary`
- `cargo reflect-bridge pack`

## What to import, not reinvent

- Rust project reflection/comptime goal metadata and future compile-time adapter experiments
- `bevy_reflect` registry / derive exports
- `facet` / `facet-reflect` associated-const and value-view substrate
- `serde_reflection` as a neighboring format-schema import whose authority must stay narrow

## Suggested `0.1` doctor warnings

- `registered_concrete_types_overclaimed_as_generic_family_support`
- `runtime_registry_requirement_not_declared`
- `compile_time_only_source_claims_runtime_mutation_surface`
- `format_projection_masquerades_as_full_type_shape`
- `adapter_losses_not_recorded`
- `mixed_source_export_missing_authority_split`

## First proving-ground scenarios

1. **Bevy registry export covering only registered concrete instantiations**
2. **Facet shape export usable as static metadata without a registry**
3. **Future const-reflection adapter producing compile-time values only**
4. **Serde format tracing remaining a format-schema projection, not a full reflection authority**
5. **Mixed-source export preserving field names but dropping richer annotations**

## What to leave for later

- final language-level reflection integration policy
- runtime mutation interop beyond coarse posture reporting
- method-level / function-signature reflection
- trait-implementation reflection
- ecosystem-wide annotation vocabularies beyond a narrow bridge core
- universal guarantees about generic-bound fidelity across all adapters
