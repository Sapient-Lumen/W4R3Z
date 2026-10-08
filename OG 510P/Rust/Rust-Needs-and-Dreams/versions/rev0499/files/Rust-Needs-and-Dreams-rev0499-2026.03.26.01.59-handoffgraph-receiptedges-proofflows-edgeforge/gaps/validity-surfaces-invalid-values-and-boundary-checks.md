# Gap: validity surfaces, invalid values, and boundary checks

## What is missing
Rust is getting better tools for talking about **safety invariants and invalid values**, but the ecosystem still lacks a portable way to publish what a crate assumes about validity at its boundaries.

Today there is no standard way to say:
- which values are invalid for a type or boundary surface (null, zero, bad discriminants, invalid niches, uninitialized bytes, impossible enum tags, layout mismatches),
- whether a conversion is valid for all bit patterns, only zeroed bytes, or only some checked subset,
- whether a boundary is checked at parse/load/FFI entry time, or simply assumes callers already upheld the invariants,
- which invariants are type-level, which are library-level, and which are runtime/environmental,
- which guarantees come from marker traits and derive macros versus runtime validation,
- how zero-copy, FFI, plugin, and unsafe-internal representations relate to one another,
- and what evidence actually ran: Miri, sanitizer runs, checked-load probes, contract checks, compile-fail vectors, or cross-language ingress tests.

That gap matters more now because Rust is no longer treating this as niche unsafe trivia. The project is actively pursuing **contract attributes**, **unsafe fields**, **comprehensive niche checks**, **sanitizer stabilization**, and **safety-critical evidence**. But crates still mostly publish validity assumptions through doc comments, marker traits, derive macros, and scattered tests.

So the missing contribution is not another one-off “safe transmute” crate.
It is a **portable way to publish validity-surface truth while the language and toolchain are building better ways to check it**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- https://rust-lang.github.io/rust-project-goals/2025h1/unsafe-fields.html
- https://rust-lang.github.io/rust-project-goals/2025h2/comprehensive-niche-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://doc.rust-lang.org/std/mem/union.MaybeUninit.html
- https://doc.rust-lang.org/reference/behavior-considered-undefined.html

## The current seam is awkward
Rust already has multiple real subcultures for validity work, but their semantics are fragmented:
- `MaybeUninit` and the reference docs explain that many types have initialization invariants and invalid values even before use,
- the niche-checks goal treats invalid-value detection as something rustc should eventually check at load-time / function entry,
- `zerocopy` publishes traits like `KnownLayout`, `FromBytes`, `TryFromBytes`, and `IntoBytes` to express layout and byte-validity claims,
- `bytemuck` publishes `Pod`, `Zeroable`, and `CheckedBitPattern` for a related but not identical validity vocabulary,
- `abi_stable` checks load-time type layout for dynamic libraries,
- `safer_ffi` tries to make foreign boundaries safer and more legible,
- Miri catches many Rust UB cases but the niche-checks goal explicitly notes that extern functions cannot be called and mixed-language binaries cannot be executed in Miri,
- and sanitizer work is becoming more official precisely because unsafe Rust and foreign code keep validity bugs alive in mixed-language systems.

So the ecosystem is not missing *techniques*.
It is missing the **artifact family that records what a boundary assumes about initialization, layout, niches, invalid values, and checked ingress**.

Sources:
- https://doc.rust-lang.org/std/mem/union.MaybeUninit.html
- https://rust-lang.github.io/rust-project-goals/2025h2/comprehensive-niche-checks.html
- https://docs.rs/zerocopy
- https://docs.rs/bytemuck
- https://docs.rs/abi_stable
- https://docs.rs/safer_ffi
- https://github.com/rust-lang/miri
- https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html

## Why this matters
This gap matters because a lot of high-value Rust work depends on validity assumptions that are currently hard to review:
1. **zero-copy parsing and binary/data interfaces** — byte-backed views need honest statements about layout, padding, endianness, and invalid bit patterns;
2. **FFI and plugin boundaries** — a value that is valid in C or C++ can still be an invalid Rust value at the boundary;
3. **unsafe abstractions** — library invariants often live in fields or internal representations that safe code can accidentally violate unless those invariants are made legible;
4. **dynamic analysis and safety evidence** — sanitizers, Miri, contracts, and future checked-load tooling all need a smaller semantic unit to attach their evidence to;
5. **mixed-language and separately compiled systems** — Rust explicitly says safety weakens when code is linked separately or across language boundaries, which means validity assumptions must be published more explicitly, not less.

A worthy contribution here is therefore not a bigger unsafe helper crate.
It is a way to treat **validity surfaces as reviewable ecosystem infrastructure**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/unsafe-fields.html
- https://rust-lang.github.io/rust-project-goals/2025h2/comprehensive-niche-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h1/safe-linking.html
- https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## What “good” looks like
A worthy contribution here is **not** one fake universal “this type is safe” badge.
It is a shared validity-surface boundary:
- one `validity-surface/v0` describing the type or boundary family and its representation lane,
- one `niche-profile/v0` describing invalid values, invalid bit patterns, discriminant restrictions, zero-validity, and initialization expectations,
- one `layout-validity-profile/v0` describing repr/layout/alignment/padding/metadata assumptions relevant to safe interpretation,
- one `boundary-ingress-profile/v0` describing where checks occur (parse time, FFI entry, load time, construction time, never) and what is assumed versus validated,
- one `unsafe-invariant-profile/v0` describing field or representation invariants that must hold beyond type-level initialization,
- one `validity-adapter-profile/v0` describing how raw bytes, foreign values, wire forms, and checked Rust forms map to one another and what is lost,
- one `validity-vector-set/v0` describing compile-fail, runtime-check, sanitizer, Miri, mixed-language, and load-time vectors,
- one `validity-check-report/v0` recording which vectors actually ran,
- and one `validity-pack/v0` bundle for docs, CI, release evidence, and archaeology.

That would let Rust teams reason about invalid values and representation assumptions using **explicit artifacts** instead of a brittle mix of derive docs, safety comments, RFC memory, and test folklore.

## Non-goals
This gap should not be used to:
- define all of Rust’s memory model or replace the Reference,
- flatten type initialization invariants, library safety invariants, FFI ABI/layout rules, and runtime UB detectors into one fake generic notion of “soundness”,
- bless one marker-trait family (`Pod`, `FromBytes`, etc.) as the official answer,
- or claim that every validity issue can be solved by one runtime checker.

The job is smaller and sharper:
**make validity surfaces legible, honest, and checkable while Rust is scaling up contracts, checked loads, mixed-language safety, and safety-critical evidence.**
