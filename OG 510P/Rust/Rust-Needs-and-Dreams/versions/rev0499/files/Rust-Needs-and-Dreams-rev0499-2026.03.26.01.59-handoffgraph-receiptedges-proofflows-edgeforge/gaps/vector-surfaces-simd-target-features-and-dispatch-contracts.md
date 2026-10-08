# Gap: vector surfaces, SIMD/scalable-lane contracts, and reviewable target-dispatch truth

## What is missing
Rust has meaningful SIMD and target-feature building blocks, but the ecosystem still lacks a **portable way to describe what a vectorized surface actually promises**.

Today there is no standard way to say:
- whether a surface is fixed-width SIMD, scalable-vector-aware, intrinsic-first, or “portable API with scalar fallback”,
- which scalar semantics are supposed to be preserved exactly and which are architecture-sensitive,
- which lane shapes, mask behaviors, reductions, saturating/wrapping rules, gather/scatter posture, or float caveats are part of the contract,
- which target features are required, optional, compile-time only, or runtime-detected,
- whether unsupported hardware means a compile error, UB if called, runtime dispatch to a fallback, or a guaranteed scalar path,
- how alignment, load/store safety, and vector-layout assumptions interact with the public API,
- whether a crate promises cross-target behavioral parity, approximate parity, or intentionally target-specific fast paths,
- and which claims were actually checked with scalar-equivalence vectors, target-selection tests, feature-gating tests, or benchmark evidence.

That gap matters because Rust is now explicitly investing in **scalable vectors** and a refined `Sized` hierarchy while `std::simd` remains nightly, `target_feature` still carries hard UB edges when used incorrectly, and today’s ecosystem already spans several incompatible-but-legitimate lanes:
- nightly `std::simd` / `core::simd` for portable SIMD,
- `std::arch` and safe wrappers like `safe_arch` for target-specific intrinsics,
- runtime multiversioning crates like `multiversion`,
- portable-but-fallback-oriented crates like `wide`,
- and domain-specific dispatch layers built on top of those pieces.

So the missing contribution is not one more SIMD crate.
It is a **reviewable vector-surface layer** for publishing vector semantics, target assumptions, dispatch/fallback posture, and evidence honestly. The normative split now lives in [`design/vector-surface-lane-map.md`](../design/vector-surface-lane-map.md): portable fixed-width, target-specific compile-time, runtime multiversion, fallback-backed, scalable-vector experimental, and adapter/consumer-import lanes must stay separate.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/arm-sve-sme.html
- https://doc.rust-lang.org/std/simd/index.html
- https://doc.rust-lang.org/reference/attributes/codegen.html#the-target_feature-attribute
- https://docs.rs/wide
- https://docs.rs/multiversion/latest/multiversion/
- https://docs.rs/safe_arch

## The current seam is awkward
Rust already has real and meaningful diversity in vectorization strategy, but most of it is published as scattered docs, cargo features, or benchmark folklore:
- `std::simd` says it is portable across targets and aims for identical behavior, but it also documents at least one notable floating-point caveat: some older architectures flush subnormal `f32` values to zero;
- `std::simd` is still nightly-only, which means many crates cannot simply standardize on it yet;
- the language reference says it is UB to call a `#[target_feature]` function on unsupported hardware unless the platform explicitly documents that as safe, and it also documents a materially different Wasm story where unsupported instructions fail at load time instead of creating the same UB risk;
- `safe_arch` deliberately works via `#[cfg()]` and compile-time CPU feature declaration only, and explicitly says it is not for runtime detection + fallback dispatch;
- `multiversion` takes the opposite posture, compiling multiple versions and selecting the best target at runtime, with `std` enabling runtime CPU detection while `no_std` falls back to compile-time dispatch only;
- `wide` advertises itself as SIMD-compatible and explicitly says that when explicit SIMD is unavailable, LLVM may vectorize or else the code becomes scalar while remaining correct;
- and the scalable-vectors work makes clear that Rust is not only dealing with today’s fixed-width lanes but also with value types whose size may be known at runtime rather than at compile time.

Those are not minor implementation details. They determine whether a library can be used in `no_std`, whether a fallback path exists, whether a performance claim is portable or target-conditional, whether a user can safely call a fast path on arbitrary hosts, and whether “vectorized” means architectural specialization or just scalar-equivalent semantics with better codegen opportunities.

Sources:
- https://doc.rust-lang.org/std/simd/index.html
- https://doc.rust-lang.org/reference/attributes/codegen.html#the-target_feature-attribute
- https://docs.rs/safe_arch
- https://docs.rs/multiversion/latest/multiversion/
- https://docs.rs/wide
- https://rust-lang.github.io/rust-project-goals/2025h1/arm-sve-sme.html
- https://rust-lang.github.io/rust-project-goals/

## Why this matters
This gap matters because vectorization choices cut across several important Rust futures at once:
1. **Performance portability** — Rust’s mission explicitly includes performance and resource usage, but today’s vector story still asks users to infer portability from docs, target flags, or source code.
2. **Language evolution** — the 2026 goals explicitly include scalable vectors, `const Sized`, and SVE/stdarch experimentation, so a lot of ecosystem design is about to become more subtle, not less.
3. **Safety and correctness** — unsupported-instruction crashes and target-feature UB are public hazards, not optimization trivia.
4. **Library interop** — users need to know whether a crate is exposing target-specific vector types, portable lane types, scalar fallbacks, or runtime-dispatched wrappers before they can compose multiple crates sanely.
5. **Evidence quality** — benchmark charts without target posture, fallback truth, or correctness vectors are not enough for serious review.

A worthy contribution here is therefore not another numerics facade, another intrinsic wrapper, or another benchmark table.
It is a way to treat vectorized surfaces as **reviewable ecosystem infrastructure**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://doc.rust-lang.org/reference/attributes/codegen.html#the-target_feature-attribute
- https://doc.rust-lang.org/std/simd/index.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## What “good” looks like
A worthy contribution here is **not** one universal SIMD API that erases meaningful differences.

It is a shared vector-surface boundary:
- one `vector-surface/v0` describing the top-level identity, intended portability lane, and whether the surface is fixed-width, scalable, intrinsic-first, or fallback-backed,
- one `lane-shape-profile/v0` for scalar element types, lane/mask shapes, reductions, and stable semantic expectations,
- one `target-feature-profile/v0` for required vs optional features, supported architectures, compile-time feature gates, and nightly/stable posture,
- one `dispatch-fallback-profile/v0` for static cfg gating, runtime detection, scalar fallback, and crash/UB hazards,
- one `alignment-layout-profile/v0` for alignment-sensitive loads/stores, repr assumptions, casting posture, and borrow/reference safety assumptions,
- one `operation-semantics-profile/v0` for saturating/wrapping rules, float/subnormal caveats, approximation posture, gather/scatter availability, and target-sensitive behavior,
- one `vector-adapter-profile/v0` for conversions between scalar, portable-SIMD, target-specific, and multiversioned surfaces,
- one `vector-vector-set/v0` for scalar-parity, target-selection, alignment, and performance-regression vectors,
- one `vector-check-report/v0` recording which vectors actually ran on which targets/features,
- and one `vector-pack/v0` bundle for docs, CI, benchmark notes, migration advice, and archaeology.

That would let Rust teams review vector claims using explicit artifacts instead of inferring them from crate names, cargo features, build flags, or “trust me, it uses SIMD” marketing.

## Non-goals
This gap should not be used to:
- define all performance engineering in Rust,
- replace `std::simd`, `std::arch`, `safe_arch`, `wide`, `multiversion`, or future SVE/SME support,
- flatten portable SIMD, target-specific intrinsics, scalable vectors, and scalar fallbacks into one fake universal vector model,
- or turn benchmark snapshots into a shallow “fast crate” leaderboard.

The job is smaller and sharper:
**make vector surfaces legible, honest, and checkable across portable, target-specific, and scalable-vector Rust.**
