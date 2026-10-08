# Design: Trait Surface lane map (ordinary static, native dyn, opaque-return/RTN, native async/RPITIT non-dyn, dyn-adapter, split-family, impl-coverage, and solver-sensitive lanes)

## Goal
Sharpen **Trait Surface Kit** so the archive stops treating “trait support” as one bucket.

Rust trait surfaces now differ materially in **dispatch posture**, **return-shape obligations**, **whether dyn works natively or only through adapters**, **how local/send or parent/child families relate**, **how blanket impls and downstream extensions behave**, and **how much of the surface is still solver- or language-sensitive**.

The archive should therefore keep trait review grounded in a lane map instead of one flattened “supports traits / supports dyn / supports async” story.

## Signals from the current ecosystem
- Rust’s 2026 flagships keep **return type notation**, **async fn in dyn trait**, **next-generation trait solver stabilization**, and **evolvable trait hierarchies** on the active roadmap. That means trait surfaces are active ecosystem infrastructure, not settled syntax trivia.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H1 async goal explicitly tracks **return type notation**, **implementable trait aliases**, **async fn in dyn Trait**, and **Dynosaur 1.0** as part of the path toward usable public async traits.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- The evolving-traits goal is directly about allowing `Receiver` above `Deref` and splitting `tower::Service` into a non-`Sync` supertrait plus a `Sync` subtrait, while setting the stage for more general trait splitting.
  https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- The next-solver goal says the new solver is intended to replace the existing implementation for proving trait bounds and normalizing associated types, fixing long-standing unsoundnesses and enabling future type-system improvements.
  https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- RFC 3654 exists because methods returning opaque types need reviewable bounds like `Send`; its motivation uses Tower’s `Service` as a live example of trait-surface pressure.
  https://rust-lang.github.io/rfcs/3654-return-type-notation.html
- RFC 3185 stabilized `async fn` in traits while explicitly leaving dyn safety for future work, which means a “native trait” claim can still hide a dyn boundary today.
  https://rust-lang.github.io/rfcs/3185-static-async-fn-in-trait.html
- Current crate/docs surfaces already expose the lane split in public: docs.rs pages now show **Dyn Compatibility** on many traits, `async-trait` openly says it makes async traits work with dyn traits through type erasure, `dynosaur` says it provides a stand-in for `dyn Trait` for async / `-> impl Trait` methods, and `trait-variant` explicitly generates local/send-style variants with a blanket impl.
  https://docs.rs/async-nats/latest/async_nats/jetstream/context/traits/trait.Requester.html
  https://docs.rs/embedded-hal-async/latest/embedded_hal_async/delay/trait.DelayNs.html
  https://docs.rs/async-trait
  https://docs.rs/dynosaur/latest/dynosaur/attr.dynosaur.html
  https://docs.rs/trait-variant/latest/trait_variant/attr.make.html

## The lanes

### 1) Ordinary static / named-return lane
This is the familiar lane where trait methods use named return types, associated types, or other ordinary static-dispatch shapes without leaning on dyn support or opaque-return tricks.

What defines it:
- ordinary static dispatch is the intended posture
- return shapes are largely explicit and named
- dyn posture is either irrelevant or secondary
- downstream reasoning is mostly about semantics, not trait-surface machinery

What it is good for:
- the baseline lane against which the other lanes can show extra obligations or losses
- trait families whose main surface is ordinary static composition

What it must **not** silently become:
- a claim that dyn is supported,
- a claim that opaque returns or sendability were reviewed,
- or a claim that split-family / solver-sensitive evolution is unimportant

### 2) Native dyn-compatible / object-safe lane
This is the lane where the trait is intended to work as `dyn Trait` with no proc-macro stand-in or boxing shim hidden behind the curtain.

What defines it:
- dyn compatibility is part of the intended public contract
- receiver and associated-item choices fit trait-object rules
- docs or rustdoc can state dyn compatibility directly

Why it deserves a separate lane:
- “supports traits” and “supports dyn” are not the same claim
- users often need to know whether trait objects are part of the real contract or just a future possibility
- the ecosystem is already surfacing dyn compatibility as visible documentation truth

Design rule:
- preserve native dyn posture separately from adapter-provided dyn posture

### 3) Opaque-return / RTN-bound lane
This is the lane where methods return `-> impl Trait`, `async fn`, or similar opaque results and the public contract depends on explicit bounds over those results.

What defines it:
- the trait’s return shape is intentionally opaque
- extra obligations like `Send`, `Sync`, `'static`, or method-specific bounds matter
- callers may need RTN-style reasoning to express what they require

Why it deserves a separate lane:
- “the method returns a future/iterator” is not enough
- reusable middleware and cross-runtime code often hinge on whether those hidden return types satisfy extra bounds
- the contract lives per method, not just per trait

Design rule:
- preserve per-method return-bound truth separately from general trait semantics

### 4) Native async / RPITIT non-dyn lane
This is the lane where the trait is native and ergonomic in static code today, but still not natively dyn-compatible.

What defines it:
- the trait uses `async fn` or `-> impl Trait` in methods
- the native language form is the desired surface
- dyn support is not yet a native guarantee

Why it deserves a separate lane:
- it is neither “ordinary named-return static trait” nor “native dyn trait”
- the archive needs to distinguish “language-native today” from “all dispatch modes solved”
- this lane often drives adapter ecosystems and migration pressure

Design rule:
- preserve native static posture and native dyn limitations separately instead of laundering them into a simple “uses async traits” claim

### 5) Dyn-via-adapter / boxing-erasure lane
This is the lane where dyn-like usability comes from proc macros, generated stand-ins, boxing, or type erasure.

What defines it:
- dyn capability is provided by an adapter
- allocations, boxing, erasure, or wrapper types may change the semantics or costs
- the adapted surface is related to, but not identical with, the native trait family

Why it deserves a separate lane:
- `async-trait`, `dynosaur`, and similar tools are strategically important precisely because they are not the same thing as native dyn support
- migration costs and semantic lossiness need to stay reviewable
- this lane is likely to persist even as the language evolves

Design rule:
- preserve adapter identity, allocation/erasure cost, and mismatches explicitly instead of calling the trait simply “dyn compatible”

### 6) Split-family / local-send / evolving-hierarchy lane
This is the lane where one trait family is intentionally represented as a parent/child, local/send, relaxed/strict, or old/new hierarchy.

What defines it:
- two or more related traits are part of the intended public surface
- blanket impls or generated variants may connect them
- migration and naming choices are part of the contract

Why it deserves a separate lane:
- evolving trait hierarchies are now an explicit roadmap seam
- libraries need to evolve without forcing a full ecosystem rewrite
- the difference between “base trait” and “stricter variant” is not cosmetic

Design rule:
- preserve family relationships and migration intent separately from one-trait semantics

### 7) Blanket-impl / adapter-extension lane
This is the lane where the surface’s real behavior depends on blanket impls, extension traits, wrapper impls, or downstream adapter relationships.

What defines it:
- implementation coverage is broader than a list of direct impls
- adapters or extension traits materially change how the surface is consumed
- overlap/coherence or sealing choices may constrain downstream use

Why it deserves a separate lane:
- trait families can look stable in docs while their useful surface actually depends on blanket or wrapper structure
- downstream users need to know whether a capability comes from the base trait, an extension trait, or an adapter
- this is often where “the same trait family” becomes lossy or partial

Design rule:
- preserve direct impls, blanket impls, extension traits, and adapter-provided capabilities as distinct truths

### 8) Solver-sensitive / acceptance-watch lane
This is the lane where the trait surface may compile or fail depending on higher-ranked reasoning, associated-type normalization, future solver behavior, or still-moving language design.

What defines it:
- compile-pass / compile-fail behavior is part of the honest story
- next-solver, HRTBs, associated-type bounds, or evolving hierarchy support materially affect the surface
- the right posture may be `watch`, `partial`, or `migration-lane`, not “ready”

Why it deserves a separate lane:
- some trait surfaces are blocked or made fragile by the solver frontier rather than by missing runtime code
- the archive already treats acceptance evidence as a first-class seam elsewhere
- teams need to separate semantic intent from currently accepted compiler patterns

Design rule:
- preserve solver-sensitive acceptance evidence separately from semantic design claims

## Review rules that follow from the lane map
1. Keep **native dyn** separate from **dyn-via-adapter**.
2. Keep **named-return static** separate from **opaque-return / RTN-bound**.
3. Keep **native async/RPITIT static use** separate from **native dyn guarantees**.
4. Keep **split-family evolution** separate from **one-trait semantics**.
5. Keep **direct impls** separate from **blanket impls, extension traits, and adapters**.
6. Keep **semantic obligations** separate from **current solver acceptance**.
7. Keep **migration intent** separate from **today’s workaround crate**.
8. Keep **per-method return-bound truth** separate from **trait-wide marketing claims**.

## What a worthy contribution should look like
The worthy contribution here is **not**:
- another trait-helper macro,
- another fake dyn-safety badge,
- another universal trait metadata blob,
- or a cargo subcommand pretending to replace the language design process.

It is a thin `cargo traitsurf` / `trait-pack/v0` layer that can preserve:
- lane identity,
- native-vs-adapter dispatch posture,
- per-method return-bound truth,
- split-family and migration relationships,
- impl / blanket / extension coverage,
- solver-sensitive acceptance evidence,
- adapter lossiness,
- and bounded downstream handoffs.

That means downstream reviewers can answer:
- *is this trait meant for static dispatch, native dyn dispatch, or dyn only through adapters?*
- *which methods carry RTN-sensitive bound obligations like `Send` or `'static`?*
- *is the async or RPITIT form native but still non-dyn today?*
- *what is the relationship between local/send or base/strict variants?*
- *which useful behaviors come from direct impls versus blanket/extension/adaptation lanes?*
- *what is semantically intended, and what is still blocked on the solver or language frontier?*

## Immediate archive consequences
Read this together with:
- `design/trait-surface-kit.md`
- `design/trait-surface-pilot-program.md`
- `gaps/trait-surfaces-dyn-posture-return-shapes-and-impl-truth.md`
- `proposals/epic-trait-surface-kit.md`

The next credible move is a ranked pilot path rather than one trait-meta abstraction: native dyn and docs-surface baseline first, opaque-return/RTN lanes second, native AFIT/RPITIT non-dyn lanes third, dyn-adapter comparison fourth, split-family evolution fifth, blanket/adaptation coverage sixth, and solver-watch acceptance evidence throughout.
