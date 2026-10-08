# Epic proposal: Const Surface Kit

## Thesis
One of the strongest missing ecosystem contributions in Rust is a **portable contract for const-evaluable library surfaces and transition posture**.

Rust is explicitly investing in richer const generics, const traits, and compile-time reflection. But the ecosystem still lacks a reviewable way to state which APIs are const-evaluable, which feature gates or bridge techniques they rely on, what compile-time costs they impose, how they fall back at runtime, and which tests actually exercised those claims across stable/nightly/MSRV matrices.

In other words: Rust needs a boring, explicit `const-pack/v0` more than it needs one more crate advertising that it is “const-friendly”.

## Why now
The timing is unusually good:
- the 2026 flagship themes explicitly include **Constify all the things**, with milestones around const-generics extensions and reflection;
- the reflection/comptime goal says ecosystem-wide derives and trait adoption create rollout friction, and proposes a `const fn`-based reflection lane to reduce that friction;
- the const-traits work says const traits are a blocker for doing more things in const contexts in general, including future heap operations;
- the expanded-const-generics work exists because users keep hitting `min_const_generics` limitations and the current `generic_const_exprs` design is not a viable stabilization path;
- the 2025 State of Rust survey says `generic const expressions` remain among the most wanted stabilizations and that resource usage is still a major productivity problem;
- the 2025 compiler-performance survey explicitly notes that stabilizing language features can remove dependence on some build scripts and proc macros, and that build performance still limits many users.

That means the next major compile-time seam is visible before it has converged.
This is exactly when a reviewable contract is most valuable.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- https://rust-lang.github.io/rust-project-goals/2025h1/const-trait.html
- https://rust-lang.github.io/rust-project-goals/2024h2/min_generic_const_arguments.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/

## What should be built
A first credible version should ship:
1. `const-surface/v0`, `const-capability-profile/v0`, `const-parameter-profile/v0`, `const-eval-cost-profile/v0`, `const-fallback-profile/v0`, `const-vector-set/v0`, `const-check-report/v0`, and `const-pack/v0`
2. one typenum / const-generics bridge pilot that records why the bridge exists and what it blocks or enables
3. one fixed-capacity / `no_std` pilot showing which constructors and adapters genuinely work in `const`
4. one compile-time parsing / formatting pilot showing evaluator-cost posture and parity with runtime lanes
5. one workaround pilot for incomplete ecosystem support (such as const-generic serialization helpers)
6. docs and CI that make channel differences, blocked language features, and fallback posture visible

The winning version is small, semantic, and transition-aware.
It should make compile-time posture legible together rather than canonizing one lane or pretending const support is a single boolean.

## Initial pilots
- **Bridge lane** — compare `typenum`, `generic-array`, and `hybrid-array` style transition posture honestly
- **Embedded lane** — record const-construction and fixed-capacity semantics for a `heapless`-style surface
- **Compile-time utility lane** — record parsing / formatting / assertions / iteration posture for `konst` / `const_format`-style crates
- **Partial-support lane** — show where downstream ecosystems still need wrappers (`serde_arrays`-style)

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document capability, parameter-model, cost, fallback, and evidence vocabulary
2. **v0.2 bridge + embedded pilots**
   - ship at least one parameter-model bridge pilot and one fixed-capacity pilot
   - show stable/nightly/MSRV differences clearly
3. **v0.3 compile-time utility + workaround depth**
   - add parsing/formatting and ecosystem workaround pilots
   - include evaluator-cost and parity reports
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one identical compile-time technique

## Success metrics
- Library authors can review const posture without reconstructing it from feature flags, compiler errors, and README caveats.
- Stable vs nightly vs MSRV differences become explicit instead of tribal knowledge.
- Transition bridges stop being invisible technical debt and become reviewable migration objects.
- Build-performance and evaluator-cost concerns become part of the design conversation early.
- Future const traits, expanded const generics, and reflection can land into an ecosystem that already records compile-time support claims.

## Archive fit
This proposal fills a real gap in the archive:
- **Macro Workflow Kit** tracks today’s proc-macro-heavy workflows and migration hints,
- **Compile Guidance Kit** handles diagnostics and compile-time UX,
- **Trait Surface Kit** handles semantic trait-family design,
- **Build Cache / Cargo Report / Footprint** cover build and resource diagnostics more broadly.

But none of those is the portable contract for **which APIs are const-evaluable, which compile-time parameter model they use, what it costs, what the runtime fallback is, and what evidence backs the claim**.
Const Surface Kit is the missing substrate for a part of Rust that the roadmap is explicitly making more important and more expressive.
