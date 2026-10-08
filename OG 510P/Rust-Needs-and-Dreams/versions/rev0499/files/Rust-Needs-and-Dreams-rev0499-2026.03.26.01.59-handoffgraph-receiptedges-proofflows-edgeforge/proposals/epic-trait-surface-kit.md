# Epic proposal: Trait Surface Kit

## Thesis
One of the strongest missing ecosystem contributions in Rust is a **portable contract for trait surfaces and trait-family evolution**.

Rust is now actively reopening major trait seams: return-type notation, async fn in dyn trait, evolvable trait hierarchies, and next-solver stabilization. But the ecosystem still lacks a reviewable way to state what a trait family means: dyn posture, return-shape guarantees, adapter cost, split-family relationships, blanket-impl assumptions, and which cases were actually checked.

In other words: Rust needs a boring, explicit `trait-pack/v0` more than it needs one more macro that says “works with traits now”.

The concrete rule for what must stay separate now lives in [`design/trait-surface-lane-map.md`](../design/trait-surface-lane-map.md), and the reference execution path now lives in [`design/trait-surface-pilot-program.md`](../design/trait-surface-pilot-program.md).

## Why now
The timing is unusually good:
- 2026 flagships explicitly target RTN stabilization, async fn in dyn trait, next-solver stabilization, and evolvable trait hierarchies;
- the evolving-traits goal is directly about making it possible to split traits like `tower::Service` and to put `Receiver` above `Deref` conceptually;
- RFC 3654 exists because trait methods returning opaques need user-visible bounds that can be expressed and reviewed;
- RFC 3185 stabilized async fn in traits, but explicitly left dyn safety for future work;
- the async goals say public async traits need RTN and implementable trait aliases, and they rely on `dynosaur` as a practical bridge;
- `async-trait` remains heavily relevant because real users need dyn-capable async trait surfaces today.

That means the next major trait-design seam is visible before it has fully converged.
This is exactly when a reviewable contract is most valuable.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- https://rust-lang.github.io/rfcs/3654-return-type-notation.html
- https://rust-lang.github.io/rfcs/3185-static-async-fn-in-trait.html
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://docs.rs/async-trait
- https://docs.rs/dynosaur

## What should be built
A first credible version should ship:
1. `trait-surface/v0`, `trait-semantics-profile/v0`, `dyn-dispatch-profile/v0`, `return-shape-profile/v0`, `impl-coverage-profile/v0`, `trait-adapter-profile/v0`, `trait-vector-set/v0`, `trait-check-report/v0`, and `trait-pack/v0`
2. one async-trait pilot comparing native AFIT, `async-trait`, and dyn-adapter posture
3. one RTN pilot showing explicit bounds on returned opaques
4. one split-family pilot for local/send or relaxed-bound traits
5. one trait-evolution pilot around a supertrait split such as `Deref` / `Receiver` or a Tower-like interface
6. docs and CI that make dyn posture, return-shape guarantees, and adaptation costs explicit

The winning version is small, semantic, and migration-aware.
It should make trait families legible together rather than prematurely canonizing one macro or one language workaround.

## Initial pilots
- **Async surface lane** — compare native `async fn` traits, boxed dyn adapters, and hybrid approaches honestly
- **Local/send lane** — show exactly what changes when a trait promises `Send` futures or thread-safe impls
- **Evolution lane** — document how a trait can split into a more general parent trait or a stricter subtrait without semantic ambiguity
- **Dyn lane** — compare native dyn support, generated dyn shims, and static-only trait posture

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document trait-family vocabulary, dyn vocabulary, and return-shape vocabulary
2. **v0.2 async and RTN pilots**
   - ship compile-fail and dyn vectors for at least one async trait family
   - show explicit bound differences in return-shape profiles
3. **v0.3 evolution and adapter depth**
   - add split-family / alias / adapter truth
   - capture migration notes and downstream compatibility evidence
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one identical implementation strategy

## Success metrics
- Library authors can review trait families without reconstructing intent from RFC memory and proc-macro docs.
- Adapter costs between static/dyn and local/send variants become visible before adoption.
- Future language features land into an ecosystem that already records what is semantic and what was workaround.
- Atlas-style guidance can recommend trait-heavy stacks with actual trait-surface evidence attached.
- Rust avoids fragmenting major trait seams into many incompatible “looks the same in docs, behaves differently in practice” families.

## Archive fit
This proposal fills a real gap in the archive:
- **Interop Commons Kit** says how shared seams emerge;
- **Pointer Surface Kit** handles pointer/reference-like semantics;
- **Lending Surface Kit** handles borrowing-aware sequence semantics;
- **Compile Guidance Kit** handles developer-facing explanations.

But none of those is the portable contract for **trait-family dyn posture, return-shape guarantees, impl coverage, and migration truth**.
Trait Surface Kit is the missing substrate for a part of Rust that the roadmap is explicitly making more dynamic and more important.
