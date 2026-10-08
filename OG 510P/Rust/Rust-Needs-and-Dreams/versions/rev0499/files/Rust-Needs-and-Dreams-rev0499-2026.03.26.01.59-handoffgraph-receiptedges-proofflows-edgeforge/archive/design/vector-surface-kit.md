# Design: Vector Surface Kit (`cargo vectorsurf`, `vector-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **vectorized/data-parallel surfaces** in Rust: portable SIMD APIs, target-specific intrinsic wrappers, runtime-multiversioned fast paths, scalar fallbacks, and future scalable-vector surfaces.

This should help answer questions like:
- is this surface fixed-width SIMD, scalable-vector-aware, intrinsic-first, or scalar-with-optional-vector-acceleration,
- what scalar semantics are expected to hold across targets,
- which target features are required, optional, nightly-only, or runtime-detected,
- can unsupported hardware safely fall back, or does calling the fast path become UB,
- what alignment and representation assumptions are public,
- what float/subnormal/saturating/reduction behaviors are promised,
- and what evidence demonstrates these claims.

It should **not** replace the vector libraries themselves, standardize one lane API, or decide how LLVM/backend codegen should behave.
It should make vector surfaces reviewable.

This design now pairs with the normative lane split in [`design/vector-surface-lane-map.md`](./vector-surface-lane-map.md) and the ranked rollout in [`design/vector-surface-pilot-program.md`](./vector-surface-pilot-program.md). The kit should be read as the artifact contract; the lane map says what must stay separate; the pilot says what to prove first.

## References (signals)
- Rust’s 2026 goals explicitly include **Sized Hierarchy and Scalable Vectors**, with milestones for `const Sized`, RFC acceptance for scalable vectors, and SVE types/intrinsics in `stdarch`. That is unusually direct evidence that vector surfaces are live ecosystem terrain rather than a solved corner.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H1 SVE/SME goal says SVE is currently unsupported, proposes type-system changes so scalable vectors can fit into Rust, and explicitly warns against overfitting to one architecture.
  https://rust-lang.github.io/rust-project-goals/2025h1/arm-sve-sme.html
- `std::simd` already exposes a portable SIMD model, but it is still nightly-only experimental.
  https://doc.rust-lang.org/std/simd/index.html
- The Rust Reference states that it is UB to call a `#[target_feature]` function on unsupported hardware unless explicitly documented safe by the platform.
  https://doc.rust-lang.org/reference/attributes/codegen.html#the-target_feature-attribute
- `multiversion` explicitly publishes the runtime-dispatch lane: compile multiple versions, detect CPU features safely, and pick the best target at runtime.
  https://docs.rs/multiversion/latest/multiversion/
- `safe_arch` explicitly publishes the compile-time-only lane: safe wrappers around intrinsics via `#[cfg()]`, not runtime detection/fallback.
  https://docs.rs/safe_arch
- `wide` explicitly publishes a fallback-oriented lane: use explicit SIMD when possible, otherwise rely on LLVM or fall back to scalar while keeping the math correct.
  https://docs.rs/wide

## Design principles
1. **Keep vector lanes distinct.** Portable SIMD, target-specific intrinsics, runtime multiversioning, and scalable vectors are related, not identical.
2. **Semantics before speed charts.** Public contracts need scalar/target behavioral truth before benchmark marketing.
3. **Fallback posture is part of the API.** “Will this still work on unsupported hardware?” is a first-class review question.
4. **Target hazards must be explicit.** UB edges, nightly requirements, and alignment assumptions cannot stay hidden in doc footnotes.
5. **Do not overfit to x86.** The scalable-vectors work is explicit that Rust should not over-specialize on one architecture.
6. **Evidence beats folklore.** Vector claims need parity vectors, target-selection tests, and performance notes that are reviewable.

## Artifact family

### 1) `vector-surface/v0`
Top-level identity for a vectorized public surface.

Fields:
- package / crate / module / surface id
- portability lane:
  - `portable-fixed-width`
  - `target-specific`
  - `runtime-multiversioned`
  - `scalar-with-vector-acceleration`
  - `scalable-vector-experimental`
- intended stability lane:
  - stable
  - nightly
  - mixed
- target families covered
- summary of primary operation families:
  - arithmetic
  - comparisons / masks
  - loads/stores
  - reductions
  - permutes/shuffles
  - gather/scatter
  - crypto / hashing / domain-specific kernels
- linked profiles and evidence

Design rule: keep the top-level surface short. Do not stuff every target flag and lane type directly into the root artifact.

### 2) `lane-shape-profile/v0`
Describes the lane model and mask model.

Fields:
- scalar element families supported
- fixed lane counts or scalable-lane posture
- mask representation / boolean-lane model
- reduction families supported
- splat / shuffle / permute posture
- gather/scatter presence or absence
- whether exposed vector types are public, hidden, or adapter-only
- scalar parity expectations

Design rule: lane shape is not the same thing as target feature requirements.

### 3) `target-feature-profile/v0`
Declares architecture/feature support.

Fields:
- architecture families
- required target features
- optional target features
- stable vs nightly feature requirements
- compile-time cfg posture
- runtime detection posture
- known unsupported combinations
- references to `stdarch`, `target_feature`, or other authoritative docs where relevant

Design rule: separate “what hardware features exist” from “how the crate chooses among them”.

### 4) `dispatch-fallback-profile/v0`
Describes how code reaches the fast path and what happens when it cannot.

Fields:
- static dispatch only / runtime dispatch / hybrid
- dispatch mechanism:
  - `cfg(target_feature)`
  - `#[target_feature]`
  - runtime CPU detection
  - manual feature flags
  - external build-system selection
- unsupported-hardware posture:
  - compile failure
  - UB if miscalled
  - safe scalar fallback
  - safe narrower-vector fallback
  - safe alternate implementation
- `std` / `no_std` notes
- testability posture
- user-facing configuration knobs

Design rule: this profile is where “crash, UB, or fallback?” becomes explicit.

### 5) `alignment-layout-profile/v0`
Describes public data-layout and memory-access assumptions.

Fields:
- alignment requirements for loads/stores
- unaligned-load support or absence
- representation / repr claims
- bytemuck/casting posture where relevant
- reference/pointer safety assumptions
- buffer stride / shape assumptions for slice APIs
- aliasing / provenance caveats if publicly relevant

Design rule: keep memory-access assumptions distinct from operation semantics.

### 6) `operation-semantics-profile/v0`
Describes public behavior that matters for correctness or portability.

Fields:
- saturating / wrapping / overflowing behavior
- floating-point caveats
- subnormal / FTZ behavior if relevant
- approximation posture for transcendental or domain-specific kernels
- NaN and signed-zero posture where relevant
- deterministic cross-target guarantees or explicit non-guarantees
- reduction / accumulation ordering caveats

Design rule: speed claims do not substitute for semantic posture.

### 7) `vector-adapter-profile/v0`
Describes conversions and migration bridges.

Fields:
- source and target surface ids
- lossless / lossy / partial conversion posture
- target-feature or nightly caveats
- fallback or boxing/allocation costs if relevant
- scalar bridge support
- migration notes for moving between `safe_arch`, `wide`, `std::simd`, vendor intrinsics, or custom wrappers

Design rule: adapters are first-class review objects. Do not bury them in changelogs.

### 8) `vector-vector-set/v0`
Portable review vectors.

Kinds of vectors:
- scalar-equivalence vector
- target-selection vector
- unsupported-hardware vector
- alignment / unaligned-load vector
- float/subnormal caveat vector
- reduction / mask vector
- fallback-regression vector
- benchmark-smoke vector

Each vector should record:
- vector id
- purpose
- relevant targets / features
- expected behavior
- severity if it fails

Design rule: keep vectors small and explicit. They are there to make surface claims testable, not to replace full benchmarks.

### 9) `vector-check-report/v0`
Attachable evidence artifact.

Fields:
- targets/features checked
- vectors run / skipped
- dispatch paths exercised
- scalar parity findings
- benchmark notes / regressions / caveats
- nightly/stable channel used
- raw attachments (bench outputs, CI logs, target-feature dumps)

### 10) `vector-pack/v0`
Bundle containing the surface, profiles, vectors, report, docs links, benchmark notes, and migration notes.

## CLI shape
- `cargo vectorsurf init` — create a starter pack for a crate/module
- `cargo vectorsurf check` — run declared vectors on selected targets/features
- `cargo vectorsurf diff` — compare packs across releases/targets
- `cargo vectorsurf explain` — show target-feature, dispatch, and fallback posture in plain language
- `cargo vectorsurf pack` — emit an attachable artifact bundle

## Review questions this makes possible
1. Does this crate guarantee scalar-equivalent correctness on unsupported hardware, or only on a checked fast path?
2. Which target features are hard requirements versus optional acceleration?
3. Are alignment-sensitive APIs safe by construction, or only by doc comment?
4. Is runtime multiversioning part of the public contract or an implementation accident?
5. Are float/subnormal/reduction semantics stable across targets?
6. Can downstream crates expose these vector types publicly without leaking nightly or target-specific commitments?

## Example v0 rollout

### Pilot A: portable API + fallback lane
Use a `wide`-style or domain crate that promises correctness with possible scalar fallback.

Artifacts should make explicit:
- portable lane shape,
- fallback posture,
- benchmark-smoke vectors,
- and any float caveats.

### Pilot B: runtime multiversion lane
Use a `multiversion`-style surface or domain crate built on it.

Artifacts should make explicit:
- runtime dispatch rules,
- required CPU detection,
- unsupported-hardware behavior,
- and which targets actually ran in CI.

### Pilot C: compile-time intrinsic lane
Use a `safe_arch`-style surface.

Artifacts should make explicit:
- compile-time-only posture,
- required `cfg(target_feature)` gates,
- alignment/reference requirements,
- and absence of runtime fallback.

### Pilot D: nightly portable/scalable lane
Use nightly `std::simd` or an experimental scalable-vector/SVE prototype.

Artifacts should make explicit:
- nightly dependence,
- lane-shape/scalable-lane posture,
- semantic caveats,
- and migration expectations toward future stabilization.

## What success looks like
The kit is working if Rust teams can answer, from one small artifact bundle:
- what kind of vector surface they are consuming,
- on which hardware/features it is supposed to work,
- whether fallback exists,
- what correctness caveats matter,
- and what evidence supports those claims.

That would be a meaningful ecosystem improvement even if no new vector instructions, crates, or compiler features shipped.

## What to avoid
- building a fake universal SIMD facade that erases meaningful differences,
- conflating target-feature requirements with dispatch/fallback policy,
- forcing every vectorized crate to expose public vector types,
- treating benchmark screenshots as sufficient evidence,
- or hard-coding the artifact model around x86 fixed-width vectors and then pretending it generalizes.


## Read this together with
- `design/vector-surface-lane-map.md`
- `design/vector-surface-pilot-program.md`
- `gaps/vector-surfaces-simd-target-features-and-dispatch-contracts.md`
- `proposals/epic-vector-surface-kit.md`
