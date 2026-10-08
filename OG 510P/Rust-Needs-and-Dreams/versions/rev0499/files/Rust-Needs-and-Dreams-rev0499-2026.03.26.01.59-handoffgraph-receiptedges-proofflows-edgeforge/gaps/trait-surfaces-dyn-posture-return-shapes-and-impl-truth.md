# Gap: trait surfaces, dyn posture, return shapes, and impl truth

## What is missing
Rust is entering a period where **trait design itself is changing shape**, but the ecosystem still lacks a reviewable way to describe what a trait surface actually promises.

Today there is no standard way to say:
- whether a trait is intended for static dispatch only, dyn dispatch now, dyn dispatch later, or generated dyn shims only,
- whether a method’s return shape is ordinary, associated-type-based, `async fn`, or `-> impl Trait`,
- whether the returned opaque types are guaranteed to be `Send`, `Sync`, `'static`, cloneable, borrowing, or executor-local,
- whether blanket impls, adapter traits, trait aliases, and split supertrait/subtrait families are part of the supported design,
- whether object-safety limitations are fundamental semantics or temporary consequences of current language/tooling limits,
- what migration path exists when one trait becomes two traits, or when a local trait and a sendable trait must coexist,
- and which claims were actually checked with compile-fail examples, dyn tests, solver-sensitive cases, or downstream adapter vectors.

That gap matters more now because this is not just “trait design taste”. Rust’s current roadmap simultaneously pushes **return type notation**, **async fn in dyn trait**, the **next-generation trait solver**, and **evolvable trait hierarchies**. Those are direct signals that traits are becoming a more active ecosystem seam: libraries will need to publish not just names and method signatures, but dyn posture, return-shape guarantees, impl coverage assumptions, and migration truth.

So the missing contribution is not another trait-helper macro.
It is a **portable way to publish trait-surface truth while the language and ecosystem are unblocking major trait features**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- https://rust-lang.github.io/rfcs/3654-return-type-notation.html
- https://rust-lang.github.io/rfcs/3185-static-async-fn-in-trait.html
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html

## The current seam is awkward
Rust already has multiple real trait-surface patterns, but their semantics are scattered across RFCs, docs, proc-macro workarounds, and project-goal pages:
- `async fn` in traits is stable, but RFC 3185 explicitly says those traits are not dyn safe today;
- RTN exists because trait methods returning opaque types need extra, user-visible bounds like `Send`;
- the 2025H1 async goals explicitly say AFIT in public traits needs RTN and implementable trait aliases to unblock real ecosystem use cases like Tower;
- `async-trait` exists because users need dyn-safe async traits now, but it changes the return strategy to boxed type erasure;
- `dynosaur` exists because the language is still growing native support for dyn dispatch over `async fn` and `-> impl Trait` methods;
- the evolving-traits goal exists because libraries need to split traits into more general supertraits or relaxed-bound variants without shattering the ecosystem;
- and the next-solver work makes clear that trait reasoning, implied bounds, and higher-ranked behavior are still an active implementation and soundness frontier.

So the ecosystem is not missing traits.
It is missing the **artifact family that records what a trait family means, how it dispatches, what its returned opaques guarantee, which impl/adaptation patterns are supported, and which cases were actually checked**.

Sources:
- https://rust-lang.github.io/rfcs/3185-static-async-fn-in-trait.html
- https://rust-lang.github.io/rfcs/3654-return-type-notation.html
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://docs.rs/async-trait
- https://docs.rs/dynosaur
- https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html

## Why this matters
This gap matters because many high-value Rust libraries already live or die by subtle trait-surface decisions:
1. **async library design** — whether returned futures are `Send`, dyn-dispatchable, executor-local, boxed, or borrowing determines whether a trait composes across runtimes and thread models;
2. **trait-family evolution** — libraries need a way to split “local” and “sendable” variants, add more general parent traits, or relax bounds without forcing ecosystem-wide rewrites;
3. **middleware and interop seams** — Tower-like trait surfaces become ecosystem infrastructure, so hidden dyn/return-shape assumptions create system-wide friction;
4. **language-adjacent crate design** — pointer-like receivers, lending traits, and future dormant-trait work all depend on trait surfaces being explicit about what is semantic versus what is tooling workaround;
5. **solver-sensitive guarantees** — blanket impls, associated-type bounds, HRTBs, and return-position opaques can look obvious in docs while still being subtle enough to break portability, object safety, or downstream composition.

A worthy contribution here is therefore not one “better trait alias” crate.
It is a way to treat trait surfaces as **reviewable ecosystem infrastructure**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://docs.rs/tower-service

## What “good” looks like
A worthy contribution here is **not** one universal supertrait, one dyn-safety score, or one proc-macro pretending today’s workaround is tomorrow’s language design.

It is a shared trait-surface boundary:
- one `trait-surface/v0` describing the trait family, purpose, dispatch intent, and attached method inventory,
- one `trait-semantics-profile/v0` describing core obligations, associated items, auto-trait or thread-safety promises, and semantic versus incidental bounds,
- one `dyn-dispatch-profile/v0` describing object-safety posture, dyn support today, generated shims, trait-object limitations, and future-native intent,
- one `return-shape-profile/v0` describing per-method return forms (`T`, associated type, GAT, `async fn`, RPITIT), extra bound expectations like `Send`, and whether boxing or type erasure occurs in adapters,
- one `impl-coverage-profile/v0` describing impl lanes, blanket impl posture, adapter traits, alias/split-trait relationships, and downstream extension assumptions,
- one `trait-adapter-profile/v0` describing how local/send, static/dyn, boxed/unboxed, or old/new trait variants map to each other and what is lost,
- one `trait-vector-set/v0` describing compile-pass, compile-fail, dyn, solver, and downstream integration vectors,
- one `trait-check-report/v0` recording which vectors actually ran,
- and one `trait-pack/v0` bundle for docs, CI, migration notes, and archaeology.

That would let Rust teams reason about trait evolution and composition using **explicit artifacts** instead of an unstable mixture of signatures, proc macros, blog memory, compiler folklore, and downstream guesswork.

The archive should now treat those as distinct review lanes rather than one trait bucket: **ordinary static/named-return + native dyn-compatible + opaque-return/RTN-bound + native async/RPITIT non-dyn + dyn-via-adapter + split/evolving family + blanket/extension coverage + solver-sensitive acceptance/watch**. The concrete rule now lives in [`design/trait-surface-lane-map.md`](../design/trait-surface-lane-map.md), and the ranked execution path now lives in [`design/trait-surface-pilot-program.md`](../design/trait-surface-pilot-program.md).

## Non-goals
This gap should not be used to:
- define Rust’s whole trait system or replace RFC work,
- flatten async traits, object-safe traits, local/send variants, blanket-impl adapters, and split hierarchies into one fake universal metadata object,
- bless one trait-helper crate or proc-macro as the official answer,
- or hide unstable design tradeoffs behind generic “supports dyn” marketing.

The job is smaller and sharper:
**make trait surfaces legible, honest, and checkable while Rust is reopening major trait seams.**
