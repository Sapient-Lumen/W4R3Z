# Design: Const Surface Kit (`cargo consteval`, `const-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **const surfaces** in Rust: which APIs are const-evaluable, which language features or transition bridges they rely on, what compile-time costs and limits they incur, what runtime fallbacks exist, and what evidence confirms those claims across stable/nightly/MSRV matrices.

This should help answer questions like:
- which constructors, methods, parsers, formatters, and adapters are usable in const contexts,
- which const parameters or associated consts are part of the public design,
- which parts of the API rely on typenum bridges, proc macros, or reflection/comptime experiments,
- what evaluator-cost or code-size risks come with the const lane,
- how runtime fallbacks compare semantically,
- and what evidence exists across channels, targets, and compiler versions.

It should **not** replace the language roadmap for const traits, expanded const generics, or reflection.
It should make ecosystem compile-time posture reviewable and comparable.

## References (signals)
- The 2026 flagship themes explicitly include **Constify all the things**, with milestones to stabilize const-generics extensions and prototype reflection.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The reflection-and-comptime goal proposes a `const fn`-based reflection scheme that only runs at compile time, explicitly motivated by the pain of requiring ecosystem-wide derives and trait adoption.
  https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- The const-traits goal says const traits are a blocker for doing more within const contexts in general, including future heap operations.
  https://rust-lang.github.io/rust-project-goals/2025h1/const-trait.html
- The expanded-const-generics work exists because users keep running into `min_const_generics` limitations and `generic_const_exprs` has fundamental design issues.
  https://rust-lang.github.io/rust-project-goals/2024h2/min_generic_const_arguments.html
- Rust’s 2025 compiler-performance survey says build performance still limits many users and explicitly notes that stabilizing language features could remove the need for some proc macros or build scripts.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The 2025 State of Rust survey says `generic const expressions` remain among the most-wanted stabilizations and that resource usage is still a major productivity problem.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `generic-array`, `hybrid-array`, `typenum`, `heapless`, `serde_arrays`, `konst`, and `const_format` show that compile-time ecosystem demand is already real and heterogeneous.
  https://docs.rs/generic-array
  https://docs.rs/hybrid-array
  https://docs.rs/typenum
  https://docs.rs/heapless/latest/heapless/mpmc/index.html
  https://docs.rs/serde_arrays
  https://docs.rs/konst
  https://docs.rs/const_format/

## Core design principles
1. **Separate language capability from crate posture.**
   A crate can be forward-looking, conservative, nightly-only, or bridge-heavy; the kit must let it say so without pretending the language is already finished.
2. **Treat costs as part of the contract.**
   Compile-time CPU, memory, recursion depth, and code-size blowups are part of the support surface.
3. **Keep transition lanes explicit.**
   Typenum bridges, proc-macro codegen, build-script generation, and runtime fallbacks are not failures; they are migration posture that should be recorded honestly.
4. **Stable/nightly/MSRV differences must be first-class.**
   Many const stories are channel- and version-sensitive.
5. **Parity is valuable but not assumed.**
   Const and runtime paths may differ in diagnostics, allocation, performance, or expressiveness.
6. **Attachments may preserve source richness.**
   The kit should point to real rustdoc, error messages, benches, and transition notes instead of flattening everything into one magic manifest.

## Shared stack note
Const Surface remains a language-foundation and compile-time kit in its own right, but it now also forms one pillar of the **Reflection Transition Stack** with [`design/reflection-surface-kit.md`](./reflection-surface-kit.md) and [`design/macro-workflow-kit.md`](./macro-workflow-kit.md).

Design rule: **Const Surface owns compile-time capability / parameter / evaluator-cost / fallback truth for reflection-adjacent lanes. It should not silently absorb runtime reflection semantics or today's proc-macro burden.**

## Artifact family

### 1) `const-surface/v0`
Describes the logical const-enabled API family.

Suggested fields:
- surface id
- crate + version + optional workspace path
- domain (`fixed-capacity`, `type-level`, `compile-time parsing`, `compile-time formatting`, `reflection bridge`, `schema/table generation`, `other`)
- audience (`embedded`, `library authors`, `proc-macro migration`, `general std-compatible`, `mixed`)
- stability posture (`stable`, `nightly`, `mixed`, `experimental`)
- high-level summary
- attached docs and examples

### 2) `const-capability-profile/v0`
Declares what parts of the API are const-evaluable.

Suggested fields:
- items covered (constructors, methods, traits, macros, associated consts, adapters)
- required channel / feature flags / MSRV
- supported contexts (`const`, `static`, `inline const`, array lengths, const generic args, type-level only)
- whether failure is compile-time panic, type error, feature-gate error, or runtime fallback
- `no_std` / `alloc` / `std` posture
- stability notes and known blockers

### 3) `const-parameter-profile/v0`
Describes the compile-time parameter model.

Suggested fields:
- const parameters used and their roles
- associated const dependencies
- whether typenum or similar bridges are used
- whether reflection/comptime data is consumed or emitted
- blocked language features (e.g. associated consts in const generics, const traits, reflection support)
- migration notes toward future language features
- interoperability notes with other parameter models

### 4) `const-eval-cost-profile/v0`
Makes evaluator / build cost reviewable.

Suggested fields:
- expected compile-time complexity class or bounded estimates
- recursion / loop / table-size posture
- likely code-size amplification or monomorphization pressure
- memory usage caveats
- diagnostics posture (good errors, brittle errors, macro-heavy, nightly-only, etc.)
- whether runtime path is recommended for large inputs
- known build-performance hazards and mitigations

### 5) `const-fallback-profile/v0`
Explains how non-const or lower-cost lanes relate.

Suggested fields:
- runtime equivalents and semantic differences
- proc-macro / build-script alternatives
- typenum / generic-array / const-generics bridge information
- whether outputs are guaranteed equal across lanes
- migration path recommendations
- known lossy or ergonomics-changing transitions

### 6) `const-vector-set/v0`
Describes the evidence matrix.

Suggested fields:
- stable, beta, nightly vectors
- MSRV vectors
- target-family vectors (`std`, `no_std`, embedded, wasm if relevant)
- parity tests between const and runtime implementations
- compile-fail / UI tests
- build-time budget tests
- docs / example compilation tests

### 7) `const-check-report/v0`
Records what actually ran.

Suggested fields:
- referenced surface + profiles
- toolchain versions used
- channels tested
- outcomes (`pass`, `fail`, `unsupported`, `inconclusive`, `skipped`)
- failure classes (`feature-blocked`, `const-eval-overflow`, `compile-time-memory`, `diagnostic-regression`, `parity-mismatch`, `other`)
- attachments to benches, UI snapshots, rustdoc JSON, CI logs
- comparability metadata for diffs

### 8) `const-pack/v0`
Bundle format:
- `const-surface/v0`
- one or more `const-capability-profile/v0`
- zero or more `const-parameter-profile/v0`
- one or more `const-eval-cost-profile/v0`
- zero or more `const-fallback-profile/v0`
- one `const-vector-set/v0`
- one or more `const-check-report/v0`
- raw attachments (rustdoc snippets, feature tables, compile-fail vectors, perf notes, migration docs)

## Reference UX: `cargo consteval`
- `cargo consteval inspect`
  - discover candidate const-evaluable items, channel gates, and transition bridges
- `cargo consteval check`
  - run declared vectors and emit `const-check-report/v0`
- `cargo consteval diff <A> <B>`
  - compare packs or versions and explain drift
- `cargo consteval doctor`
  - explain missing const evidence, unstable blockers, or suspicious overclaims
- `cargo consteval pack`
  - bundle a `const-pack/v0`

`cargo consteval` should begin as an orchestrator / validator / packer. It should avoid becoming a new macro system, a const-eval engine, or a replacement for rustc.

## Default policy
- **Surface-first, not feature-hype-first.**
- **Costs and limits are part of support truth.**
- **Transition bridges are first-class, not embarrassing details.**
- **Stable/nightly divergence is allowed but must be explicit.**
- **Parity claims require evidence.**
- **Unsupported and not-yet-possible are valid outcomes.**

## What the kit should provide to others
- **Embedded / fixed-capacity teams:** a way to publish which constructors and helpers work in `const` and at what cost.
- **Library authors:** a reviewable picture of how const APIs affect MSRV, public design, and migration.
- **Tool builders:** attachable artifacts for compile-time feature matrices rather than brittle rustdoc scraping alone.
- **Macro / proc-macro transition work:** a place to record when reflection or const-fn lanes begin to replace code generation.
- **Future language/toolchain work:** a landing zone for const traits, expanded const generics, and compile-time reflection once they mature.

## Overlap boundaries
- **Not Macro Workflow Kit:** that kit inventories proc-macro workflows and migration hints broadly; this kit models the const-evaluable surface itself.
- **Not Compile Guidance Kit:** that kit owns developer-facing diagnostics and extension hooks; this kit owns compile-time capability and cost truth.
- **Not Trait Surface Kit:** semantic trait-family design lives there; this kit only records whether const trait posture changes callable surfaces.
- **Not Pointer or Lending Surface Kits:** those own ownership/borrowing semantics; this kit only records their const-evaluable posture if relevant.
- **Not Build Cache / Cargo Report Kits:** those own build diagnostics broadly; this kit contributes one compile-time feature/cost family.

## Hard problems (explicitly scoped)
1. **Language churn**
   - v0 must record blockers and channel differences without freezing transient experiments into dogma.
2. **Evaluator-cost comparability**
   - compile-time cost is real but difficult to normalize; v0 should start with honest profiles, not fake precision.
3. **Parity drift**
   - const and runtime implementations may diverge in subtle ways; the kit must make that visible.
4. **Type-level vs value-level confusion**
   - typenum / const-generic / reflection / macro lanes must remain distinguishable.
5. **Overclaiming “const support”**
   - it must be easy to say “constructor is const, mutation path is not” or “stable supports small cases only”.

## Evaluation plan
Pilot on:
1. one typenum / const-generics bridge (`generic-array` / `hybrid-array`-style),
2. one fixed-capacity `no_std` lane (`heapless`-style),
3. one compile-time parsing / formatting lane (`konst` / `const_format`-style),
4. one ecosystem workaround lane where const-generic support is partial (`serde_arrays`-style),
5. one migration note set tied to reflection/comptime aspirations.

Success bar:
- projects can publish const posture without inventing new README conventions,
- reviewers can tell what is stable vs nightly vs blocked,
- compile-time cost and fallback posture become visible before teams overcommit,
- and future const-traits / const-generics / reflection work can land into a ready-made evidence surface.
