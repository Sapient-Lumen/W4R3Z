# Design: Reflection Transition Pilot Program

## Goal
Prove that the **Reflection Transition Stack** can turn today's reflection and macro ecosystems into reviewable, comparable, and migratable lanes before upstream compile-time reflection fully lands.

This pilot program is deliberately about **transition honesty**:
- what a subject uses today,
- what introspection it actually exposes,
- what proc-macro, orphan-rule, and registry burden it still pays,
- what downstream adapters depend on that lane,
- and whether a future reflection/comptime lane would really simplify anything.

## Why this now
- Rust's 2026 flagship work keeps **prototype reflection** active, which means ecosystem migration pressure is no longer hypothetical.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The reflection-and-comptime goal explicitly positions compile-time reflection as a way to reduce derive lock-in while also saying proc-macro derives are historically hard to debug and bootstrap.
  https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- The macro-improvements goal aims to make many proc-macro use cases declarative instead, specifically to improve build times and reduce dependencies.
  https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- The compiler-performance survey says stabilizing language features could remove some proc macros or build scripts altogether.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The Bevy/gamedev follow-up in the August 2025 program-management update makes the userland pressure concrete: reflection is a broad pain point, `derive(Reflect)` workflows are difficult to write/debug, and orphan-rule limitations still force wrappers and partial coverage.
  https://blog.rust-lang.org/inside-rust/2025/09/11/program-management-update-2025-08/

The proposal-layer candidate for turning these pilots into a buildable ecosystem contribution remains [`proposals/epic-reflection-transition-stack.md`](../proposals/epic-reflection-transition-stack.md).

## What this pilot is not
This is not:
- a commitment to one reflection runtime,
- a language proposal choosing Rust's final reflection design,
- a “replace all derives now” program,
- or a benchmark contest between reflection libraries.

It is a ranked set of pilots that produce honest migration and adapter evidence.

## Shared anti-patterns to reject
1. **derive erasure theater** — claiming compile-time reflection solves a workflow without showing what proc-macro inventory, cost, and debug burden actually disappears.
2. **inspect-equals-mutate confusion** — treating object-safe inspection as if it implied safe rebuilding or mutation.
3. **schema-equals-reflection confusion** — treating traced or exported schemas as if they were a universal type-introspection substrate.
4. **registry amnesia** — hiding ordering, deduplication, static-registration, or platform caveats behind “auto registration”.
5. **orphan-rule disappearance** — pretending foreign-type and std-type friction vanishes before a target lane truly addresses it.
6. **future-lane overclaim** — promising migration to core reflection before a consumer lane has been compared with today's alternatives.

## Ranked pilots

### 1) Structured-observability lane
**Subjects**
- `valuable`
- `tracing` / subscriber-side `valuable` support

**Question**
Can the stack describe an **inspect-only** reflection lane for telemetry without overclaiming mutation, reconstruction, registry richness, or schema guarantees?

**Artifacts to require**
- `macro-pack/v0` only if derives/macros are materially involved
- `reflection-acquisition-profile/v0`
- `reflection-value-access-profile/v0`
- `reflection-adapter-profile/v0` for telemetry/observability
- explicit “inspect-only” and experimental-feature notes

**Why first**
This is the cleanest case where reflection-like value access already matters, but the capability boundary is intentionally narrow and should stay narrow.

### 2) Runtime-editor / registry lane
**Subjects**
- `bevy_reflect`
- one registry-dependent runtime/editor/config scenario

**Question**
Can the stack describe runtime metadata, mutation posture, registration semantics, and foreign-type/orphan-rule caveats honestly enough for editor/UI/config consumers?

**Artifacts to require**
- `reflection-shape-profile/v0`
- `reflection-value-access-profile/v0`
- `reflection-registry-profile/v0`
- `reflection-adapter-profile/v0`
- optional macro inventory if derives are part of the workflow
- explicit coverage notes for std/foreign types and wrapper strategies where relevant

**Why second**
This exercises the hard parts that object-safe inspection skipped: mutation, registration, platform caveats, adapter richness, and missing coverage pressure.

### 3) Compile-time shape / schema lane
**Subjects**
- `facet`
- `serde_reflection`

**Question**
Can the stack compare **associated-const shape metadata** and **schema-tracing outputs** without pretending they are interchangeable or that either one is already general reflection?

**Artifacts to require**
- `reflection-acquisition-profile/v0`
- `reflection-shape-profile/v0`
- optional `const-capability-profile/v0`
- explicit adapter profiles for schema/codegen/export consumers
- lossiness notes where schema-trace omits general reflection semantics

**Why third**
This is where future compile-time reflection pressure will be felt most strongly, so the archive should force honest comparison now.

### 4) Derive-heavy migration lane
**Subjects**
- one proc-macro-heavy crate/workspace with real derive usage
- optional declarative-macro alternative where relevant

**Question**
Can the stack produce a useful migration plan that separates:
- what macros currently acquire,
- what reflection lane could replace,
- what orphan-rule/workaround pressure would remain,
- what const/comptime support is still missing,
- and what downstream adapters would need to change?

**Artifacts to require**
- `macro-inventory/v0`
- `macro-cost-report/v0`
- `macro-debug-report/v0` where useful
- `macro-migration-hints/v0`
- matching reflection and const profiles for the target lane
- explicit unsupported-lane / watch-wait notes

**Why fourth**
This is where the stack becomes strategically useful instead of merely descriptive.

### 5) Future core-reflection comparison lane
**Subjects**
- any experimental compile-time reflection prototype as it becomes available

**Question**
Can the archive compare future core reflection against today's lanes without declaring premature victory?

**Artifacts to require**
- `reflection-acquisition-profile/v0` with `comptime-experiment`
- `const-capability-profile/v0`
- `const-eval-cost-profile/v0`
- side-by-side adapter notes against existing runtime/object-safe/schema lanes
- consumer-import notes documenting what truly became simpler

**Why last**
The archive should wait for real prototypes rather than inventing fake certainty.

## Pack shape to exercise during pilots
Every pilot should aim to emit or simulate:
- one `reflection-transition-subject/v0`;
- imported `macro-pack/v0`, reflection-surface, and const-surface attachments as appropriate;
- optional `reflection-transition-diff/v0` when a migration or lane comparison is part of the exercise;
- at least one consumer-specific `reflection-transition-handoff/v0`;
- explicit watch/wait notes when a target lane is not yet adoption-ready.

## Success criteria
The pilot succeeds when:
- reflection lanes can be compared without flattening them,
- downstream consumers can say exactly what kind of introspection they require,
- macro-heavy subjects get credible migration reports instead of slogans,
- runtime-registry and foreign-type caveats stay visible,
- future compile-time reflection can be evaluated against established artifacts,
- and the archive can honestly say “wait” when a lane is not yet ready.

## Expected downstream consumers
- observability / debug tooling
- schema and codegen pipelines
- config / CLI / editor / inspector generators
- framework/plugin ecosystems with runtime registries
- migration / maintenance review for derive-heavy crates

## Rollout guidance
Start narrow and comparative.
Do not widen to a universal registry or universal reflection manifest before the first three pilots produce honest differences.

## Strategic outcome
If this pilot works, the ecosystem gets a practical answer to a hard near-future question:

**When compile-time reflection arrives, how do we migrate real Rust ecosystems without losing sight of macro costs, orphan-rule/workaround pressure, runtime capabilities, registry semantics, and downstream adapter needs?**
