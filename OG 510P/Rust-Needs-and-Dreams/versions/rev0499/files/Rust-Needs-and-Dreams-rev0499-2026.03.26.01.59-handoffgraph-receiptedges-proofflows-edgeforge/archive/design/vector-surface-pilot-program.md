# Design: Vector Surface pilot program (portable fixed-width, target-specific compile-time, runtime multiversion, fallback-backed, scalable-vector experimental, and consumer-import lanes)

## Goal
Turn **Vector Surface Kit** into a ranked pilot program that proves Rust teams can publish honest vector-surface semantics without waiting for portable SIMD or scalable vectors to fully stabilize.

This pilot should make the archive prefer **lane-aware vector packs, target-feature profiles, dispatch/fallback reports, semantic-caveat notes, and small checked vector sets** over another intrinsic wrapper, one benchmark badge, or one generic “SIMD-ready” summary.

## Why this now deserves a pilot
The strategic timing is unusually strong:
- Rust’s 2026 flagships keep **Sized Hierarchy and Scalable Vectors** active, including refined `Sized`, `const Sized`, scalable-vector RFC progress, SVE types/intrinsics in `stdarch`, and early SME design work.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H1 SVE/SME goal says SVE is currently unsupported in Rust, calls for a nightly experiment, and explicitly warns against overfitting the design to one architecture.
  https://rust-lang.github.io/rust-project-goals/2025h1/arm-sve-sme.html
- `std::simd` already documents a portable fixed-width lane that compiles on every target, remains nightly-only, and carries real semantic caveats on some older architectures.
  https://doc.rust-lang.org/std/simd/index.html
- The Rust Reference keeps `#[target_feature]` hazards explicit, including UB risk on unsupported hardware outside target families like Wasm where load-time failure changes the safety story.
  https://doc.rust-lang.org/reference/attributes/codegen.html#the-target_feature-attribute
- Current crates already expose the lane split in practice: `safe_arch` is compile-time-only, `multiversion` is runtime-dispatch-first, and `wide` is fallback-backed.
  https://docs.rs/safe_arch
  https://docs.rs/multiversion/latest/multiversion/
  https://docs.rs/wide

See the normative lane split in [`design/vector-surface-lane-map.md`](./vector-surface-lane-map.md).

## Pilot artifacts
The pilot should exercise a small but durable artifact family:
- `vector-surface/v0`
- `lane-shape-profile/v0`
- `target-feature-profile/v0`
- `dispatch-fallback-profile/v0`
- `alignment-layout-profile/v0`
- `operation-semantics-profile/v0`
- `vector-adapter-profile/v0`
- `vector-vector-set/v0`
- `vector-check-report/v0`
- `vector-pack/v0`

Every stage should prefer a few small target-aware vectors and explicit caveats over giant benchmark dumps.

## Ranked rollout

### Stage 1 — fallback-backed stable lane
Subjects:
- one `wide`-style surface or domain crate whose public claim is correctness with optional acceleration
- one scalar-equivalence and fallback-regression vector set

Why first:
- it gives the archive the most honest portability story first
- it proves the pack can represent “fast path optional, correctness mandatory” without needing nightly or exotic hardware
- it keeps the pilot grounded in user-visible fallback behavior rather than only feature catalogs

Outputs:
- one baseline `vector-surface/v0`
- one `dispatch-fallback-profile/v0` showing scalar or narrower-vector fallback
- one report distinguishing explicit-SIMD, LLVM-autovectorized, and scalar outcomes where relevant

### Stage 2 — target-specific compile-time lane
Subjects:
- one `safe_arch`-style wrapper or narrowly scoped `std::arch` surface
- one alignment-sensitive or layout-sensitive vector API

Why second:
- this makes hard target-feature gates and representation assumptions explicit early
- it proves the archive can talk about target-specific public commitments without pretending runtime fallback exists
- it exposes the difference between “safe wrapper” and “portable behavior”

Outputs:
- one `target-feature-profile/v0`
- one `alignment-layout-profile/v0`
- one vector set showing compile-time-only gating and unsupported-target posture

### Stage 3 — runtime multiversion lane
Subjects:
- one `multiversion`-style function family
- one runtime detection / target-selection example

Why third:
- this is the clearest lane where dispatch behavior itself is the contract
- it forces runtime CPU detection, `std`/`no_std`, and unsupported-target behavior into first-class review artifacts
- it creates the comparison users actually need against compile-time-only and fallback-first surfaces

Outputs:
- one `dispatch-fallback-profile/v0` marked runtime-dispatched
- one target-selection vector set
- one report explaining which implementations actually ran in CI or on sampled hardware

### Stage 4 — nightly portable fixed-width lane
Subjects:
- one nightly `std::simd` surface
- one operation family where target-specific intrinsics differ semantically from portable SIMD

Why fourth:
- this establishes the “portable but still nightly and caveat-bearing” lane cleanly
- it keeps the archive from collapsing nightly portable SIMD into either intrinsics or scalar fallback stories
- it provides a disciplined place for subnormal, reduction, and mapping-to-instruction caveats

Outputs:
- one lane-shape and operation-semantics pair for a portable-SIMD surface
- one vector set covering scalar parity and at least one documented semantic caveat
- one report separating nightly-channel posture from surface semantics

### Stage 5 — scalable-vector experimental lane
Subjects:
- one SVE or scalable-vector prototype / watch subject
- one explicit migration note toward future stabilized scalable-vector support

Why fifth:
- this is where the pilot proves it does not overfit to today’s fixed-width lanes
- it creates a disciplined place for `watch`, `prototype`, and `migration-lane` posture
- it lets the repo track live Rust language work without pretending the ecosystem contract already exists in stable form

Outputs:
- one `vector-surface/v0` marked scalable-vector experimental
- one lane-shape profile that records runtime-known lane-size posture explicitly
- one migration/watch note tied to Rust-project-goals progress

### Stage 6 — downstream consumer-import lane
Subjects:
- one scientific / media / crypto / parsing consumer that imports vector truth rather than owning it
- one adapter or feature-leak note showing what downstream users can and cannot conclude

Why sixth:
- this is where the vector pack proves it matters beyond isolated kernels
- it keeps downstream productization stacks from silently re-owning vector semantics
- it makes bounded handoffs real before the archive widens vector claims into support or release stories

Outputs:
- one `vector-adapter-profile/v0`
- one consumer-import note with exact versus partial versus unsupported conclusions
- one explicit handoff to Perf / Support / Scientific or Media consumers

## Practical design rules
- Do not skip from Stage 1 straight to one universal vector schema.
- Every stage should attach at least one **partial**, **unsupported**, or **caveat-bearing** outcome so the pack proves honesty, not just success.
- Every stage should preserve exact lane meaning from [`design/vector-surface-lane-map.md`](./vector-surface-lane-map.md).
- Target-feature truth should never be buried inside benchmark prose.
- If a lane is still nightly or prototype-only, say `watch` / `migration-lane` instead of implying convergence.

## What success looks like
A good pilot outcome would let a reviewer answer:
- whether a surface is portable fixed-width, target-specific, runtime-multiversioned, fallback-backed, or scalable-vector experimental,
- which target features are hard requirements versus optional acceleration,
- whether unsupported hardware crashes, becomes UB if miscalled, or safely falls back,
- what alignment/layout or operation-semantics caveats actually matter,
- what was checked on which targets/features,
- and what downstream crates may legitimately conclude from the evidence.

If the pilot cannot answer those questions with artifacts, the archive is still leaning on vector folklore.

## Boundaries
- **Benchmark Evidence Kit** still owns broader benchmark-lane imports and baseline policy.
- **Scientific Productization Stack** still owns array/tensor/dataset/model/backend/support composition above imported vector truth.
- **Media Surface Kit** and **Cryptography Surface Kit** still own codec/algorithm/runtime claims above imported vector lanes.
- **Support Envelope Kit** still owns bounded user-facing support claims rather than raw vector semantics.

## Near-term recommendation
Treat this pilot as the next concrete move for the archive’s performance-adjacent language frontier: fallback-backed and target-specific truth first, runtime dispatch second, nightly portable SIMD third, scalable-vector watch work fourth, and only then broader downstream productization imports.
