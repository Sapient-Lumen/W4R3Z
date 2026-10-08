# Design: Vector Surface lane map

## Goal
Sharpen **Vector Surface Kit** into an explicit lane map so future revisions stop flattening Rust SIMD and data-parallel work into one fake “SIMD support”, “vector portability”, or “accelerated numerics” verdict.

The missing contribution is not one universal intrinsic wrapper or one blessed vector API.
It is a reviewable boundary that keeps today’s materially different vector lanes legible enough to compare, adapt, and hand off.

## Why this needs a lane map now
Rust already has multiple serious vector families, but they do not mean the same thing:
- `std::simd` is a **portable fixed-width** lane that compiles on every target, is still nightly-only, and still documents concrete semantic caveats like subnormal-`f32` flush-to-zero on some older architectures.
- `std::arch` and crates like `safe_arch` are **target-specific compile-time** lanes whose meaning is bound to architecture and `#[cfg(target_feature)]` posture rather than runtime dispatch.
- crates like `multiversion` are **runtime multiversion** lanes that compile several implementations and safely choose among them at runtime.
- crates like `wide` are **fallback-backed** lanes whose public story is “use explicit SIMD when possible, otherwise keep the math correct and fall back”.
- the active SVE/SME and scalable-vector work is an **experimental scalable-vector** lane, not just a bigger fixed-width SIMD lane.
- downstream scientific, media, crypto, and systems crates often act as **adapter/consumer-import** lanes rather than owning every vector semantic themselves.

That means the next ecosystem contribution should preserve **lane identity + target/dispatch truth + semantic caveats + evidence** above those pieces.

## The lanes

### 1) Portable fixed-width lane
Use for surfaces whose primary identity is **portable SIMD with fixed lane counts** and whose contract aims to hold across targets.

Typical examples:
- nightly `std::simd` / `core::simd`
- future stabilized portable-SIMD-style surfaces

Keep explicit:
- nightly versus stable posture
- fixed lane-count families and mask model
- scalar-equivalence expectations
- documented semantic caveats such as subnormal handling or operation-level divergence from target-specific intrinsics

Do **not** quietly reinterpret this lane as target-specific intrinsics or as a guarantee that every operation maps to one machine instruction.

### 2) Target-specific compile-time lane
Use for surfaces whose primary identity is **architecture-specific intrinsics or wrappers selected at compile time**.

Typical examples:
- `std::arch`
- `safe_arch`
- domain crates exposing `cfg(target_feature)`-gated fast paths without runtime dispatch

Keep explicit:
- architecture family and required target features
- compile-time-only gating posture
- unsafe or alignment-sensitive assumptions
- absence of runtime negotiation or fallback unless separately attached

Do **not** flatten this lane into portable SIMD just because a wrapper is safe to call after configuration.

### 3) Runtime multiversion lane
Use for surfaces whose primary identity is **multiple compiled implementations plus runtime target selection**.

Typical examples:
- `multiversion`
- custom runtime CPU-detection dispatch tables

Keep explicit:
- detection mechanism
- selected target families/features
- `std` versus `no_std` posture
- what happens on unsupported hardware or missing detection support

Do **not** hide dispatch rules inside benchmarks or macro defaults.

### 4) Fallback-backed compatibility lane
Use for surfaces whose primary identity is **prefer vector acceleration when available while preserving correctness through narrower or scalar fallback paths**.

Typical examples:
- `wide`
- domain crates whose public promise is scalar-correctness first and vector acceleration second

Keep explicit:
- when explicit SIMD is used
- when LLVM-autovectorization is only opportunistic
- when the code becomes scalar
- whether reductions, transcendental ops, or floating-point behavior change across fast and fallback lanes

Do **not** market this lane as identical to portable SIMD or runtime multiversion dispatch.

### 5) Scalable-vector experimental lane
Use for surfaces whose primary identity is **vector values whose size is known at runtime rather than at compile time**, or other emerging scalable-vector language/library work.

Typical examples:
- SVE nightly experiments
- future SME-adjacent work
- RFC/prototype surfaces exploring scalable-vector support in Rust’s type system

Keep explicit:
- nightly-only or prototype posture
- type-system / `Sized` hierarchy assumptions
- architecture generality versus architecture-specific experimentation
- migration expectations toward future stabilized forms

Do **not** force this lane into fixed-width metadata just because today’s ecosystem mostly knows fixed-width vectors.

### 6) Adapter / consumer-import lane
Use for crates or workflows whose main value is **bridging, consuming, or embedding** vector lanes rather than defining all vector semantics natively.

Typical examples:
- scientific or media crates importing vector kernels
- crypto or parsing crates hiding target-specific kernels behind a stable API
- migration bridges between scalar code, portable-SIMD code, and target-specific fast paths

Keep explicit:
- which source and destination lanes are involved
- whether adaptation is exact, copyful, partial, or lossy
- what target or nightly commitments leak through
- what the consumer imported versus redefined

Do **not** let a successful downstream use erase the underlying vector-lane differences.

## Cross-cutting truths that must stay separate
Every lane can still carry multiple distinct truths:
- **lane-shape / mask truth**
- **target-feature truth**
- **dispatch / fallback truth**
- **alignment / layout / representation truth**
- **operation-semantics truth**
- **check / benchmark / evidence truth**
- **bounded consumer imports**

Those are not interchangeable. A target-specific lane can share arithmetic intent with a portable lane while differing radically on selection, fallback, alignment, or semantic caveats.

## Preferred archive interpretation
When the archive discusses Vector Surface going forward, prefer:
- **portable fixed-width lane**
- **target-specific compile-time lane**
- **runtime multiversion lane**
- **fallback-backed compatibility lane**
- **scalable-vector experimental lane**
- **adapter / consumer-import lane**

over:
- one fake “SIMD support” verdict
- one fake “uses vectors” claim
- one universal intrinsic facade proposal
- silently importing all vector meaning into scientific, media, or crypto product stories

## What a worthy contribution should look like in practice
A thin `cargo vectorsurf` / `vector-pack/v0` layer should:
- publish which lane or lanes a crate is actually claiming,
- attach separate lane-shape, target-feature, dispatch/fallback, alignment/layout, and operation-semantics artifacts,
- report exact versus partial versus lossy adapters,
- record what was checked on which targets/features,
- and hand bounded vector facts to Scientific / Media / Crypto / Support / Perf consumers.

The bar is not another SIMD runtime.
The bar is making lane-aware vector claims reviewable.

## Read this together with
- `design/vector-surface-kit.md`
- `design/vector-surface-pilot-program.md`
- `gaps/vector-surfaces-simd-target-features-and-dispatch-contracts.md`
- `proposals/epic-vector-surface-kit.md`
