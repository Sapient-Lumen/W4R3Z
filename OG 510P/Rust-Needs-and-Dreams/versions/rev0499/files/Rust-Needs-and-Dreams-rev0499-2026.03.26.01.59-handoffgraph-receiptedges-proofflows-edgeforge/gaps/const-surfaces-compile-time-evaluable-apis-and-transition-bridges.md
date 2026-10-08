# Gap: const surfaces, compile-time-evaluable APIs, and transition bridges

## What is missing
Rust is explicitly moving toward a world where **more useful work happens in const contexts**: richer const generics, const traits, and compile-time type introspection / reflection are all now on the official roadmap. But the ecosystem still lacks a portable way to publish what a library’s **const surface** actually is.

Today there is no standard way to say:
- which functions, methods, constructors, and adapters are const-evaluable on stable versus nightly,
- which parts of an API are plain `min_const_generics`, which rely on typenum bridges, and which are blocked on associated consts, generic const args, or const traits,
- whether a crate’s const lane produces values, type-level witnesses, precomputed tables, generated strings, or build-time failures,
- what the evaluator-cost posture is (recursion depth, compile-time memory, table size, code-size amplification, expansion cost, panic/diagnostic ergonomics),
- what the fallback path is when const evaluation is unavailable or too expensive,
- how proc-macro, type-level, and const-fn based approaches relate during transition,
- and what evidence actually ran across MSRVs, targets, stable/nightly, and compile-time vs runtime parity tests.

That gap matters more now because Rust is no longer treating const as a curiosity. The 2026 flagship themes explicitly include **"Constify all the things"**, with milestones around const-generics extensions and reflection, while the const-traits work says const traits are a blocker for doing more in const contexts in general, including heap operations. Meanwhile the expanded-const-generics work exists because users keep running into `min_const_generics` walls and the current `generic_const_exprs` design is too broken to serve as the ecosystem’s transition story.

So the missing contribution is not another numerics crate or one more proc-macro convenience layer.
It is a **portable way to publish const-surface truth while the language is widening what compile-time Rust can do**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- https://rust-lang.github.io/rust-project-goals/2025h1/const-trait.html
- https://rust-lang.github.io/rust-project-goals/2024h2/min_generic_const_arguments.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/

## The current seam is awkward
Rust already has multiple real subcultures for compile-time work, but their semantics are fragmented:
- `typenum` still provides type-level numbers and operators, and explicitly ships const-generics-friendly mappings,
- `generic-array` remains a living bridge because stable const generics still cannot express some common patterns like associated-const-based sizes,
- `hybrid-array` explicitly positions itself as an incremental transition path between typenum-style constraints and const generics,
- `heapless` shows const construction and fixed-capacity/no-allocator data structures are practical and valuable today,
- `serde_arrays` exists because Serde still lacks out-of-the-box const-generic array support,
- `konst` and `const_format` show real demand for compile-time parsing, iteration, formatting, assertions, and diagnostics,
- and the reflection/comptime goal explicitly says proc-macro derives have historically been hard to debug and bootstrap from scratch, motivating const-fn-based alternatives.

So the ecosystem is not missing *compile-time tricks*.
It is missing the **artifact family that records which compile-time lane a crate supports, where it hits language limitations, what it costs, and how it transitions forward**.

Sources:
- https://docs.rs/typenum
- https://docs.rs/generic-array
- https://docs.rs/hybrid-array
- https://docs.rs/heapless/latest/heapless/mpmc/index.html
- https://docs.rs/serde_arrays
- https://docs.rs/konst
- https://docs.rs/const_format/
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html

## Why this matters
This gap matters because a lot of valuable Rust work increasingly depends on compile-time posture that is hard to review:
1. **embedded / `no_std` / fixed-capacity APIs** — teams need to know which constructors and operations work in `const` and which silently fall back to runtime or allocation;
2. **public library design** — const-stable constructors and adapters affect API shape, MSRV policy, downstream ergonomics, and migration cost;
3. **compile-time data generation** — tables, parsers, formatters, and validators need honest statements about evaluator cost and compile-time failure behavior;
4. **transition planning** — crates built on `typenum`, `generic-array`, proc macros, or partial const-generics need a reviewable path toward future const-traits / expanded-const-generics / reflection capabilities;
5. **productivity and build performance** — Rust’s 2025 compiler-performance survey says build performance still limits many users, and explicitly notes that stabilizing language features could reduce dependence on build scripts and proc macros.

A worthy contribution here is therefore not a bigger pile of const helpers.
It is a way to treat **const surfaces as reviewable ecosystem infrastructure**.

Sources:
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://docs.rs/heapless/latest/heapless/mpmc/index.html
- https://docs.rs/generic-array
- https://docs.rs/hybrid-array

## What “good” looks like
A worthy contribution here is **not** one fake universal "const-ready" badge.
It is a shared const-surface boundary:
- one `const-surface/v0` describing the API family and compile-time lane,
- one `const-capability-profile/v0` describing which APIs are const-evaluable, under which channels / features / MSRVs,
- one `const-parameter-profile/v0` describing array sizes, const parameters, associated-const usage, typenum bridges, reflection needs, and blocked language features,
- one `const-eval-cost-profile/v0` describing evaluator complexity, recursion / loop posture, memory / code-size amplification, panic / diagnostic behavior, and build-performance caveats,
- one `const-fallback-profile/v0` describing runtime equivalents, proc-macro / build-script alternatives, and migration notes,
- one `const-vector-set/v0` describing stable/nightly/MSRV/build-mode parity vectors,
- one `const-check-report/v0` recording which vectors actually ran,
- and one `const-pack/v0` bundle for docs, CI, release archaeology, and migration planning.

That would let Rust teams reason about const-evaluable APIs using **explicit artifacts** instead of a brittle mix of feature-gate notes, README caveats, compiler error screenshots, and type-level folklore.

## Non-goals
This gap should not be used to:
- replace const traits, const generics, or reflection language design,
- flatten value-level const evaluation, type-level numerics, proc-macro generation, and build-script codegen into one fake generic notion of "compile-time support",
- bless one ecosystem lane (`typenum`, `generic-array`, proc macros, const-fn helpers) as the official answer,
- or pretend evaluator cost and build-performance consequences do not matter.

The job is smaller and sharper:
**make const surfaces legible, honest, and checkable while Rust is scaling up compile-time expressiveness.**
