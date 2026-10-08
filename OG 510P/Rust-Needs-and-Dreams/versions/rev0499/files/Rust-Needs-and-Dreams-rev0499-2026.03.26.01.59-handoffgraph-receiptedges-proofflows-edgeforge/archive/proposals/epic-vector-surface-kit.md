# Epic proposal: Vector Surface Kit

## Thesis
Rust is entering a period where **vectorized surfaces are getting more important and more diverse at the same time**:
- the project goals explicitly include scalable vectors and SVE/stdarch experimentation,
- nightly `std::simd` already offers a portable SIMD lane,
- `target_feature` still exposes hard safety/UB edges,
- and the ecosystem already spans compile-time-only intrinsics, runtime multiversioning, and scalar-fallback-oriented abstractions.

What is still missing is a **shared review/evidence layer above those pieces**.

So the epic contribution here is not another SIMD crate.
It is **Vector Surface Kit**: one portable way to publish lane identity, lane shape, target-feature posture, dispatch/fallback behavior, alignment/layout assumptions, semantic caveats, and checked evidence for vectorized Rust surfaces. This epic now pairs with [`design/vector-surface-lane-map.md`](../design/vector-surface-lane-map.md) and [`design/vector-surface-pilot-program.md`](../design/vector-surface-pilot-program.md).

## Why this is worthy
This is worthy because it helps Rust in several high-value ways at once:
1. **performance portability** — users can tell whether a crate is “portable SIMD”, “target-specific fast path”, or “scalar fallback with acceleration” without source-diving;
2. **language/library transition support** — the ecosystem gets a bridge while `std::simd` and scalable vectors are still evolving;
3. **safer target-feature usage** — unsupported-hardware UB and target assumptions become explicit review objects;
4. **better composition** — downstream crates can decide whether to expose, wrap, or hide target-specific vector commitments;
5. **better evidence** — benchmark claims gain target/fallback/correctness context.

## Signals
- Rust in 2026 includes **Sized Hierarchy and Scalable Vectors** with milestones for `const Sized`, scalable-vector RFC progress, and SVE types/intrinsics in `stdarch`.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The SVE/SME goal says scalable vectors need type-system changes and explicitly warns against overfitting the design to one architecture.
  https://rust-lang.github.io/rust-project-goals/2025h1/arm-sve-sme.html
- `std::simd` is portable and behaviorally consistent across targets in most respects, but is still nightly-only and documents concrete caveats like FTZ/subnormal behavior on some older architectures.
  https://doc.rust-lang.org/std/simd/index.html
- The Rust Reference says miscalling `#[target_feature]` code on unsupported hardware is UB.
  https://doc.rust-lang.org/reference/attributes/codegen.html#the-target_feature-attribute
- `multiversion`, `safe_arch`, and `wide` demonstrate that the ecosystem already has multiple legitimate lanes with meaningfully different portability and fallback stories.
  https://docs.rs/multiversion/latest/multiversion/ ; https://docs.rs/safe_arch ; https://docs.rs/wide

## Proposed scope
Ship:
1. `vector-surface/v0`, `lane-shape-profile/v0`, `target-feature-profile/v0`, `dispatch-fallback-profile/v0`, `alignment-layout-profile/v0`, `operation-semantics-profile/v0`, `vector-adapter-profile/v0`, `vector-vector-set/v0`, `vector-check-report/v0`, and `vector-pack/v0`
2. `cargo vectorsurf` for init/check/diff/explain/pack workflows
3. one portable/fallback pilot, one runtime-multiversion pilot, and one compile-time-intrinsic pilot
4. one nightly/scalable-vector experimental pilot if practical
5. CI/report patterns that attach target-feature and parity evidence to releases/PRs

Do **not** ship:
- a universal vector runtime,
- a replacement for `std::simd` or `std::arch`,
- a mandatory benchmark framework,
- or a fake “SIMD-ready” badge with no semantics.

## Early roadmap
### v0.1 — fallback-backed and compile-time lanes
- finalize the lane map and pilot contract
- prove one `wide`-style fallback-backed surface and one `safe_arch`-style compile-time surface
- make scalar parity, target-feature gates, and unsupported-target posture reviewable

### v0.2 — runtime multiversion lane
- add one `multiversion`-style pilot
- validate runtime CPU-detection, `std`/`no_std`, and target-selection reporting
- ship `cargo vectorsurf explain` with clear dispatch/fallback summaries

### v0.3 — nightly portable fixed-width lane
- add one nightly `std::simd` pilot
- validate portable fixed-width lane-shape and operation-semantics caveats
- attach small target-aware vectors instead of only benchmark notes

### v0.4 — scalable-vector watch lane and downstream imports
- model one SVE/scalable-vector experimental subject or watch artifact
- prove the schema does not overfit to today’s fixed-width lanes
- add one bounded downstream consumer-import story

## What success looks like
Within a few revisions, the repo should be able to point to a credible story for:
- how Rust crates honestly publish vectorized public support,
- how to compare portable SIMD vs target-specific intrinsics vs runtime multiversioning,
- how to review target hazards and fallback posture,
- and how scalable-vector work can enter the ecosystem without every crate inventing its own metadata vocabulary.

That would count as a real ecosystem contribution because it reduces confusion and review cost **before** and **during** the next wave of vector-feature stabilization.
