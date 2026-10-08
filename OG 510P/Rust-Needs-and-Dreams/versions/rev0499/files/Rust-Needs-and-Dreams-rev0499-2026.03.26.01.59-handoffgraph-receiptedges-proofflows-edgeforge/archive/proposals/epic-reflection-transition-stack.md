# Epic Proposal: Reflection Transition Stack (`cargo reflect-transition` + `reflection-transition-pack/v0`)

## One-sentence pitch
Give Rust one thin, portable boundary for comparing and migrating reflection lanes so teams can keep **current proc-macro burden, runtime reflection semantics, visit-only/schema lanes, foreign-type coverage limits, and future compile-time reflection posture** distinct instead of flattening them into one fake “reflection support” story.

## Deliverables
- reference command:
  - `cargo reflect-transition`
- schemas:
  - `reflection-transition-brief/v0`
  - `reflection-transition-subject/v0`
  - `reflection-transition-pack/v0`
  - `reflection-transition-diff/v0`
  - `reflection-transition-handoff/v0`
- adapters/importers for:
  - `macro-pack/v0`
  - `reflection-surface/v0`
  - `reflection-acquisition-profile/v0`
  - `reflection-shape-profile/v0`
  - `reflection-value-access-profile/v0`
  - `reflection-registry-profile/v0`
  - `reflection-adapter-profile/v0`
  - `const-surface/v0`
  - `const-capability-profile/v0`
  - `const-eval-cost-profile/v0`
  - `const-fallback-profile/v0`
- docs:
  - runtime reflection vs inspect-only guide
  - schema/shape lane comparison guide
  - derive-heavy migration guide
  - foreign-type/orphan-rule pressure guide
  - future core-reflection comparison guide
  - consumer-lossiness guide for observability / editor / config / codegen / assistant readers

## Why now (signals)
- Rust's 2026 flagship work explicitly includes **prototype reflection**, making reflection an active language-adjacent frontier.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The reflection-and-comptime goal proposes a compile-time reflection path, says proc-macro derives have historically been hard to debug and bootstrap, and says crates like `bevy_reflect` and `facet` would still exist afterwards with different goals and methods.
  https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- The macro-improvements goal explicitly argues that replacing many proc-macro use cases with declarative macros can improve build times and reduce dependency chains.
  https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- The 2025 compiler-performance survey says stabilizing language features could remove some proc macros or build scripts, tying reflection transition directly to everyday build pain.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The August 2025 program-management update says Bevy and gamedev users raised reflection as a major pain point, and explains why today's derive-based reflection is difficult to write/debug and limited by orphan-rule coverage.
  https://blog.rust-lang.org/inside-rust/2025/09/11/program-management-update-2025-08/
- `bevy_reflect` remains a runtime reflection lane with dynamic interaction and a real `TypeRegistry` / `TypeRegistration` model.
  https://docs.rs/bevy_reflect/latest/bevy_reflect/
- `facet` offers a `SHAPE` associated const for type-shape metadata, which is a different lane from runtime registries.
  https://docs.rs/facet/latest/facet/
- `valuable` provides object-safe value inspection, and `tracing`'s support for it is explicit, opt-in, and experimental rather than a universal reflection substrate.
  https://docs.rs/valuable/latest/valuable/
  https://docs.rs/tracing/latest/tracing/field/index.html
- `serde_reflection` traces serialization structure to derive format descriptions and recommends storing them under version control to detect unintended changes.
  https://docs.rs/serde-reflection/latest/serde_reflection/

## The missing seam
Rust now has real ingredients for reflection transition, but they still live in different planes:
- macro inventory/cost/debug truth,
- runtime reflection and registry truth,
- visit-only observability truth,
- schema/shape extraction truth,
- foreign-type / orphan-rule workaround pressure,
- and compile-time / const aspirations.

What it still lacks is the stack-level boundary that says:
1. which lane is this subject using today;
2. what proc-macro and registry burden is still being paid;
3. what kind of introspection is actually available;
4. which downstream adapters depend on that lane;
5. what target lane is being considered;
6. what foreign-type or cross-crate coverage problems remain;
7. and what a maintainer or downstream consumer may honestly conclude now.

Without that, teams still have to reconstruct migration and comparison stories from crate docs, benchmark folklore, issues, and framework-specific knowledge.

## Reference CLI shape
- `cargo reflect-transition record`
  - emit `reflection-transition-subject/v0` for one concrete subject and consumer set
- `cargo reflect-transition attach-macro`
  - import macro workflow evidence for the subject
- `cargo reflect-transition attach-reflection`
  - import runtime / visit-only / schema / registry evidence for the subject
- `cargo reflect-transition attach-const`
  - import compile-time capability/cost/fallback evidence for the target or comparison lane
- `cargo reflect-transition diff --against <prior-pack|ref|path>`
  - emit `reflection-transition-diff/v0`
- `cargo reflect-transition render --for <observability|editor|config|codegen|maintenance|assistant>`
  - emit `reflection-transition-handoff/v0`
- `cargo reflect-transition pack`
  - produce `reflection-transition-pack/v0`
- `cargo reflect-transition verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace reflection crates, proc-macro tooling, schema generators, or future language design work.

## What `reflection-transition-pack/v0` should contain
- `manifest.json`
- `reflection-transition-brief.json`
- one or more `reflection-transition-subject.json`
- imported macro-workflow evidence pointers or attachments
- imported reflection-surface evidence pointers or attachments
- imported const-surface evidence pointers or attachments
- optional `reflection-transition-diff.json`
- one or more `reflection-transition-handoff.json` summaries
- checksums, provenance, freshness, and generator identity

## Design principles
- **Current burden first.** Future compile-time reflection should not erase today's macro or registry costs.
- **Lane identity stays explicit.** Runtime reflection, visit-only inspection, schema tracing, and associated-const shape are not interchangeable.
- **Coverage gaps matter.** Orphan-rule and foreign-type pressure belong in the migration story rather than in caveats no one imports.
- **Registries are semantics, not decoration.** Ordering, discovery, deduplication, and platform caveats belong in the pack.
- **Watch/wait is a valid result.** The stack should be good at saying “not yet.”
- **Consumers import bounded conclusions.** Observability, config/editor, codegen/schema, maintenance, and assistant consumers each need their own lossy summaries.
- **The stack remains thin.** A portable contract is enough; no universal reflection engine is required.

## Early implementation order
1. visit-only observability lane
2. runtime registry/editor lane
3. schema/shape comparison lane
4. derive-heavy migration lane
5. future core-reflection comparison lane

That order follows the actual pressure in the ecosystem: first keep narrow lanes honest, then compare richer runtime lanes, then confront shape/schema ambiguity, then make migration planning useful, and only then compare future language-native reflection.

## Non-goals
- a universal reflect trait;
- a new runtime reflection crate;
- a derive helper empire;
- a registry framework that tries to own every ecosystem;
- declaring compile-time reflection victorious before real consumer lanes are compared.

## Success bar
This becomes worthy when a maintainer or downstream consumer can answer:
- what exact reflection lane is under review;
- what proc-macro burden still exists;
- what metadata and value access the lane actually provides;
- what registry/discovery semantics matter;
- what downstream adapters truly depend on that lane;
- what compile-time / const posture is real versus merely desired;
- what foreign-type/orphan-rule coverage remains problematic;
- what changed versus a prior lane or version;
- and whether the honest conclusion is adopt, compare further, migrate partially, or wait,

without flattening the story into one vague “reflection support” badge.

## Read this with
- `gaps/reflection-transition-lane-comparison-macro-burden-and-core-reflection-migration.md`
- `design/reflection-transition-stack.md`
- `design/reflection-transition-pilot-program.md`
- `design/reflection-surface-kit.md`
- `design/macro-workflow-kit.md`
- `design/const-surface-kit.md`
