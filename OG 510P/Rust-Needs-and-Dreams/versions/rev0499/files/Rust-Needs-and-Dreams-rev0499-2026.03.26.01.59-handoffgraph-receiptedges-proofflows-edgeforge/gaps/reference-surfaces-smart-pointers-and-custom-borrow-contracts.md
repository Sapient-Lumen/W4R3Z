# Gap: reference surfaces, smart pointers, and custom borrow contracts

## What is missing
Rust is now explicitly trying to make **user-defined smart pointers feel as natural as `&` and `&mut`**, but the ecosystem still lacks a reviewable way to describe what pointer-like surfaces actually promise.

Today there is no standard way to say:
- whether a surface is shared, uniquely-owned, clone-on-write, pinned, foreign-backed, intrusive, or merely reference-shaped,
- whether identity and equality are about value equality, allocation identity, or metadata-insensitive pointer identity,
- whether “cheap clone” means aliasing, clone-on-write preparation, weak-pointer dissociation, or deferred deep copy,
- whether uniqueness claims are safe checks, unsafe obligations, temporary witnesses, or runtime-only facts,
- whether projection is shared, mutable, pinned, or move-projecting with a husk/teardown story,
- whether method receivers, coercions, unsizing, and dyn dispatch are supported natively, via derives, or not at all,
- whether mutation/exclusivity claims are Rust-reference semantics, foreign/runtime-defined semantics, or intentionally weaker,
- and which guarantees were actually checked with vectors, compile-fail cases, Miri, or downstream adapter tests.

That gap matters more now because this is no longer just library-inventor hobbyism. The Rust project’s 2025H2 flagship theme is “Beyond the `&`”, aimed at making custom smart pointers as ergonomic as built-in references. The 2026 flagships continue that lane with field projections, reborrow traits, and in-place-initialization alignment. RFC 3519 says custom smart pointers remain second-class citizens today, RFC 3621 exists so custom smart pointers can participate in trait objects, and Rust-for-Linux still depends on unstable smart-pointer-related features like `arbitrary_self_types` and `derive_coerce_pointee`.

So the missing contribution is not just “a nice smart-pointer crate”.
It is a **portable way to publish pointer-surface truth while the language is opening this frontier**.

Sources:
- https://rust-lang.github.io/rust-project-goals/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rfcs/3519-arbitrary-self-types-v2.html
- https://rust-lang.github.io/rfcs/3621-derive-smart-pointer.html
- https://rust-lang.github.io/rust-project-goals/2025h2/Rust-for-Linux-language.html

## The current seam is awkward
Rust already has many pointer forms, but their semantics are scattered across std docs, RFCs, project-goal pages, and crate-specific lore:
- `Arc::ptr_eq` exposes allocation identity distinct from value equality and explicitly ignores dyn-pointer metadata,
- `Arc::make_mut` can either reuse uniquely-owned state, clone the inner value, or dissociate `Weak` pointers,
- `Arc::get_mut`, `Arc::get_mut_unchecked`, and nightly `Arc::is_unique` expose different grades of uniqueness evidence and aliasing assumptions,
- `Pin` is a wrapper around some pointer `Ptr`, not a standalone ownership story, and its projection/invalidation rules are subtle enough that pin ergonomics is a flagship goal,
- field projections are an active design problem precisely because modified references and custom pointer-like wrappers conceptually support subfield access without ordinary `Deref`,
- arbitrary self types exist because custom smart pointers need receiver ergonomics without necessarily producing `&T` or `&mut T`,
- derive-smart-pointer exists because custom smart pointers still need explicit support for coercions and trait objects,
- and Rust-for-Linux / foreign-language cases need wrappers that intentionally do **not** claim ordinary Rust-reference exclusivity.

So the ecosystem is not missing pointer experimentation.
It is missing the **artifact family that records identity, aliasing, uniqueness, projection, coercion/receiver posture, and lifecycle truth in one reviewable place**.

Sources:
- https://doc.rust-lang.org/std/sync/struct.Arc.html
- https://doc.rust-lang.org/std/rc/struct.Rc.html
- https://doc.rust-lang.org/std/pin/index.html
- https://doc.rust-lang.org/std/pin/struct.Pin.html
- https://rust-lang.github.io/rust-project-goals/2025h2/field-projections.html
- https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
- https://rust-lang.github.io/rfcs/3519-arbitrary-self-types-v2.html
- https://rust-lang.github.io/rfcs/3621-derive-smart-pointer.html

## Why this matters
This gap matters because many high-value Rust workloads want pointer-like surfaces that are more expressive than bare references but more reviewable than custom unsafe folklore:
1. **foreign-language and FFI references** — wrappers for C++, Python, kernels, handles, or intrusive data structures want receiver ergonomics without pretending to be `&mut T`;
2. **ref-counted and cheaply-cloneable APIs** — ergonomic ref-counting is an active Rust priority, but the ecosystem still lacks a portable way to state aliasing, uniqueness, weak-pointer, and clone-on-write semantics;
3. **pinned and projection-heavy code** — async, generators, and in-place initialization all sharpen the need for honest pin/projection/move-projection/destruction contracts;
4. **custom reborrowable references** — the reborrow-traits work explicitly aims to let Rust-for-Linux and `reborrow`-style ecosystems move toward core solutions;
5. **future convergence** — once “Beyond the `&`” features land, Rust will need a disciplined way to compare and migrate pointer abstractions instead of spawning many incompatible “almost-reference” worlds.

A worthy contribution here is therefore not a single blessed pointer crate.
It is a way to treat pointer semantics as **reviewable ecosystem infrastructure**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
- https://rust-lang.github.io/rust-project-goals/2025h2/pin-ergonomics.html
- https://rust-lang.github.io/rust-project-goals/2025h2/field-projections.html
- https://rust-lang.github.io/rust-project-goals/2024h2/ergonomic-rc.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## What “good” looks like
A worthy contribution here is **not** one universal smart-pointer trait, one unsafe abstraction empire, or one attempt to settle the Rust memory model in a cargo subcommand.

It is a shared pointer/reference surface boundary:
- one `pointer-surface/v0` describing the subject, pointer family, identity rules, and supported operations,
- one `alias-uniqueness-profile/v0` describing sharing, cheap-clone meaning, weak/cycle posture, uniqueness witnesses, and mutation gates,
- one `projection-family-profile/v0` describing shared/mutable/pinned/move projection, reborrow behavior, invalidation, and husk/drop cleanup posture,
- one `receiver-coercion-profile/v0` describing method-receiver, coercion, unsizing, and dyn-dispatch posture,
- one `pointer-transition-profile/v0` describing conversions between pointer forms and where allocation, cloning, lifetime erasure, runtime checks, or safety preconditions appear,
- one `pointer-vector-set/v0` describing golden cases for identity, clone/share/unique/drop/projection/reborrow/dyn behavior,
- one `pointer-check-report/v0` recording which vectors were actually checked,
- and one `pointer-pack/v0` bundle for docs, CI, migration notes, and archaeology.

That would let Rust teams reason about custom pointer surfaces using **explicit artifacts** instead of a mixture of trait docs, unsafe comments, issue threads, RFC memory, and accidental transitive knowledge.

The next credible archive move is now a ranked pilot program rather than more schema expansion: shared-ownership truth first, pinned projection second, foreign-reference truth third, receiver/dyn posture fourth, and transition/migration consumers fifth. See [`design/pointer-surface-pilot-program.md`](../design/pointer-surface-pilot-program.md).

## Non-goals
This gap should not be used to:
- define Rust’s entire aliasing or provenance model,
- flatten `Rc`, `Arc`, `Pin`, foreign references, intrusive pointers, handle wrappers, and custom reference types into one fake universal trait,
- bless one “correct” smart-pointer library,
- or hide unsafe invariants behind vague “reference-like” marketing.

The job is smaller and sharper:
**make pointer-like surfaces legible, honest, and checkable while Rust is trying to make them first-class.**
