# Design: Trait Surface Kit (`cargo traitsurf`, `trait-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **trait surfaces and trait families** in Rust: ordinary traits, async traits, RPITIT-heavy traits, dyn-oriented interfaces, local/send split families, adapter traits, and traits that are evolving toward new supertrait or subtrait structures.

This should help answer questions like:
- is this trait meant for static dispatch, dyn dispatch, both, or only via generated shims,
- what forms do its method returns take and what extra bounds are required on them,
- which bounds are semantic guarantees versus temporary workarounds,
- how do local/send or old/new trait variants relate,
- what blanket impl or downstream extension assumptions exist,
- and what evidence shows the trait family behaves as claimed.

It should **not** replace the trait system, subsume trait aliases, or settle solver design debates in a cargo subcommand.
It should make trait surfaces reviewable and comparable.

This kit should now be read together with [`design/trait-surface-lane-map.md`](./trait-surface-lane-map.md) and [`design/trait-surface-pilot-program.md`](./trait-surface-pilot-program.md), so future revisions keep native dyn posture, opaque-return obligations, dyn adapters, family splits, and solver-sensitive acceptance distinct instead of narrating one fake “trait support” story.

## References (signals)
- The 2026 flagships explicitly aim to stabilize return type notation, async fn in dyn trait, the next-generation trait solver, and evolvable trait hierarchies. That is direct evidence that trait surfaces are an ecosystem seam, not a solved syntax detail.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The evolving-traits goal is specifically about unblocking changes like `Deref: Receiver` and splitting `tower::Service` into a non-`Sync` supertrait and a `Sync` subtrait; it also says the design should pave the way for more general trait splitting.
  https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- The next-solver goal says the new solver is intended to replace the existing type-system components for proving trait bounds and normalizing associated types, to fix long-standing unsoundnesses and unblock future improvements.
  https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- RFC 3654 defines RTN so users can write bounds like `T: Trait<method(..): Send>` for `async fn` and `-> impl Trait` methods in traits.
  https://rust-lang.github.io/rfcs/3654-return-type-notation.html
- RFC 3185 explicitly says traits using `async fn` are not dyn safe today and explains their desugaring to anonymous associated types / GAT-like machinery.
  https://rust-lang.github.io/rfcs/3185-static-async-fn-in-trait.html
- The 2025H1 async goal says AFIT in public traits needs RTN and implementable trait aliases to unblock Tower-like use cases, and it treats `dynosaur` as part of the near-term path for dyn dispatch.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- Existing crates prove the workaround demand is real: `async-trait` makes async trait methods work with dyn traits by boxing/type erasure; `dynosaur` allows dynamic dispatch over traits using `async fn` or `-> impl Trait` while preserving static dispatch elsewhere.
  https://docs.rs/async-trait
  https://docs.rs/dynosaur
- `tower-service` shows a single trait surface can become a major ecosystem boundary, which makes split-trait evolution and explicit adapter truth especially important.
  https://docs.rs/tower-service

## Core idea
Treat a trait family as a **reviewable surface with explicit dispatch posture, return-shape truth, impl coverage, and migration/adaptation metadata**.

Instead of asking people to infer all of that from signatures and docs, publish compact artifacts that say:
- what the trait is for,
- what each method returns in semantic terms,
- which bounds on returned opaques are promised,
- what dyn story exists today,
- what adapter or split-family story exists,
- and what vectors were actually checked.

## Artifact family

### 1) `trait-surface/v0`
Top-level description of a trait or trait family.

Fields should include:
- trait id / version
- human name and crate path
- purpose / domain summary
- whether this is a single trait, split family, alias-backed family, or adapter surface
- dispatch intent (static / dyn / mixed / shimmed)
- method inventory with stable ids
- linked profiles and packs

### 2) `trait-semantics-profile/v0`
Describes semantic obligations and stable meaning.

Fields should include:
- supertraits and associated items
- semantic obligations versus incidental/current bounds
- thread-safety / auto-trait posture if promised as API contract
- mutation / borrowing / ownership expectations tied to methods
- required invariants for implementors
- known unstable or provisional semantics

### 3) `dyn-dispatch-profile/v0`
Describes trait-object posture and limitations.

Fields should include:
- dyn safe now / not dyn safe / dyn safe via adapter / future-native target
- object-safety blockers
- generated-shim strategy (`async-trait`, `dynosaur`, custom boxing, etc.) if used
- unsizing / receiver / trait-object limitations
- lifetime or allocation consequences of dyn adaptation
- feature-gate / toolchain requirements

### 4) `return-shape-profile/v0`
Describes per-method output forms.

Fields should include:
- method id
- return mode (`T`, associated type, GAT, RPITIT, `async fn`, boxed-erased, adapter-generated)
- required or promised bounds on the returned type (`Send`, `Sync`, `'static`, etc.)
- borrowing / lending posture
- allocation / boxing / type-erasure consequences
- executor / runtime assumptions if relevant
- whether the guarantee is native, macro-emulated, or adapter-provided

### 5) `impl-coverage-profile/v0`
Describes how implementation space is structured.

Fields should include:
- direct impl lanes
- blanket impl posture
- extension points intended for downstreams
- split-trait / alias / relaxed-bound relationships
- overlap/coherence-sensitive areas
- “sealed” or intentionally-closed posture
- migration notes when family structure changes

### 6) `trait-adapter-profile/v0`
Describes mappings between trait surfaces.

Fields should include:
- source/target trait ids
- lossless / lossy / partial status
- changes in dyn posture
- changes in return-shape guarantees
- boxing / allocation / thread-safety / borrow-erasure costs
- required helper macros, wrapper types, or glue impls
- unsupported cases

### 7) `trait-vector-set/v0`
Golden vectors for trait-surface behavior.

Fields should include:
- vector id
- fixture/setup description
- compile-pass expectations
- compile-fail expectations
- dyn-dispatch expectations
- RTN / return-bound expectations
- blanket-impl / downstream-adapter expectations
- negative and unsupported cases

### 8) `trait-check-report/v0`
Records what was actually exercised.

Fields should include:
- traits / adapters checked
- vectors run / skipped
- pass/fail/partial status
- observed mismatches
- rustc / cargo / toolchain details
- attached compile-fail logs, UI tests, downstream examples, or minimal repros

### 9) `trait-pack/v0`
Bundle of the above plus docs, migration notes, examples, issue links, and CI pointers.

## CLI shape
`cargo traitsurf` should be a thin orchestrator, not a replacement type-system tool.

Potential commands:
- `cargo traitsurf init` — scaffold trait-surface metadata
- `cargo traitsurf export` — emit trait-surface and profile artifacts
- `cargo traitsurf check` — run vectors over selected traits/adapters
- `cargo traitsurf diff` — compare semantic changes across versions
- `cargo traitsurf pack` — bundle a `trait-pack/v0`

The tool should favor references to source, tests, docs, and existing compile-fail fixtures rather than giant generated snapshots.

## Initial targets
A first credible version should start where the seam is already undeniably real:
1. **Async trait pilot**
   - one native `async fn in trait` example
   - one `async-trait` adapter example
   - one `dynosaur` / dyn-adapter example
2. **RTN + bound pilot**
   - one trait where returned futures or iterators need explicit `Send` or similar guarantees
3. **Trait-family evolution pilot**
   - one `trait_variant` or Tower-style local/send split example
   - one conceptual supertrait split like `Deref` / `Receiver`
4. **Solver-sensitive pilot**
   - one case involving associated-type bounds, HRTBs, or blanket impl sensitivity that deserves explicit vectors

The kit should support both **promotion** (this trait family is ready to serve as ecosystem substrate) and **deferral** (the native language story is still moving, so adapters remain the honest answer).

The ranked execution path should now follow the lane map: native dyn baseline first, opaque-return/RTN obligations second, native AFIT/RPITIT non-dyn third, dyn-adapter comparison fourth, split-family evolution fifth, blanket/adaptation coverage sixth, and solver-sensitive acceptance evidence throughout.

## What good adoption looks like
A good v1 does not need to solve all future trait design in Rust.
It needs to prove that the ecosystem can publish honest trait-surface truth.

Success would look like:
- one report that makes dyn posture and return-shape guarantees obvious,
- adapter profiles that reveal when “supports dyn” really means boxing/type erasure,
- vectors catching drift in RTN bounds or split-family guarantees,
- migration notes that let trait families evolve without folklore,
- and one Atlas or domain guide that can recommend a trait-heavy stack with real attached evidence.

## Boundaries with other archive proposals
- **Interop Commons Kit** is about when neutral shared seams emerge across crates; Trait Surface Kit is the contract for making a trait family itself explicit and reviewable.
- **Compile Guidance Kit** helps explain errors and lints around traits, but it does not define trait-surface semantics.
- **Pointer Surface Kit** covers custom receiver/reference-like semantics; Trait Surface Kit covers the trait obligations and dispatch/return-shape story above those receivers.
- **Lending Surface Kit** covers sequence/item-yield semantics; Trait Surface Kit can describe the trait family that exposes such semantics but does not replace the sequence-specific contract.
- **Public API Kit** covers semver/public-surface truth at release time; Trait Surface Kit focuses on the deeper behavioral meaning of trait families and their adapters.

## Failure modes to avoid
- inventing a universal metadata shape that erases real trait-family differences;
- treating current proc-macro shims as if they were the same thing as native language support;
- hiding allocation, boxing, or `Send` requirements behind a simple “dyn supported” badge;
- flattening supertrait evolution, blanket impls, and adapter-based compatibility into one fake notion of “implements the same trait”;
- or pretending solver-sensitive behavior is obvious from prose.
