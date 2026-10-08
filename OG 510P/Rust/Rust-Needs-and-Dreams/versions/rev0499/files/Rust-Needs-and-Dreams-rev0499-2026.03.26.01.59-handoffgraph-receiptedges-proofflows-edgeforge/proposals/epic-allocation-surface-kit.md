# Epic proposal: Allocation Surface Kit

## Thesis
One of the more worthy Rust ecosystem contributions now would be a **portable review layer for allocation surfaces**.

Not another allocator benchmark suite.
Not another arena crate.
Not another global-allocator wrapper.

The missing layer is a way to publish, diff, and verify:
- what memory resource model a crate actually depends on,
- whether allocation failure aborts, panics, or returns an error,
- whether reclamation happens one object at a time, by reset, or by bulk teardown,
- whether destructors run when storage is reclaimed,
- which stable/nightly/interoperability lane is required,
- and what evidence shows those claims are real.

That contribution would be unusually leveraged because it can serve parsers, compilers, graph systems, embedded code, high-performance servers, `no_std` libraries, and allocator-aware collections at once.

## Why this could be epic
Rust now has unusually broad allocation diversity, but not yet a shared review layer:
- std still exposes a process-global allocator lane,
- std’s generic allocator APIs and `*_in` constructors are real but remain nightly,
- `allocator-api2` exists as a stable mirror because the ecosystem wants this now,
- containers like `hashbrown` already compose with that lane,
- arena and bump crates remain common where locality or bulk teardown matter,
- and high-level users still need a way to describe memory behavior honestly.

That is exactly the moment when a **surface contract** becomes more valuable than one more implementation.

Sources:
- https://doc.rust-lang.org/std/alloc/trait.Allocator.html
- https://doc.rust-lang.org/std/vec/struct.Vec.html
- https://doc.rust-lang.org/beta/alloc/boxed/struct.Box.html
- https://docs.rs/allocator-api2
- https://docs.rs/hashbrown
- https://docs.rs/bumpalo
- https://docs.rs/typed-arena/
- https://docs.rs/mimalloc

## What the contribution should look like in practice
The contribution should probably be a **tool + schema family + reference adapters + example packs**.

### 1) Tooling
A `cargo allocsurf` command that can:
- scaffold the artifact family,
- inspect a workspace for likely allocation lanes,
- run bounded OOM/reset/drop/interop vectors,
- diff support claims over time,
- and export one portable `allocation-pack/v0`.

### 2) Schemas
At minimum:
- `allocation-surface/v0`
- `memory-resource-profile/v0`
- `container-allocation-profile/v0`
- `region-lifetime-profile/v0`
- `oom-failure-profile/v0`
- `allocation-adapter-profile/v0`
- `allocation-vector-set/v0`
- `allocation-check-report/v0`
- `allocation-pack/v0`

### 3) Reference adapters
The project becomes much more real if it ships reference adapters for:
- process-global allocator wrappers,
- allocator-generic collections via nightly `Allocator`,
- stable `allocator-api2`-based interop,
- bump/arena lanes,
- one id-arena or graph-arena family.

### 4) Example packs
Ship real examples that deliberately differ in shape:
- a process-global allocator override crate,
- an allocator-generic container crate,
- a parser/compiler-style bump arena,
- a graph/id arena with bulk teardown and handle semantics.

Those examples should prove the surface layer can represent disagreement honestly instead of smoothing it away.

## Design principles
1. **Do not lie about resource identity.** Global allocators, arena resets, and injected allocators are not the same story.
2. **Do not lie about failure posture.** Fallible APIs and abort-on-OOM lanes must remain visibly different.
3. **Keep reset and destructor truth first-class.** Region reset that skips `Drop` is not “normal deallocation”.
4. **Keep interop posture first-class.** Stable `allocator-api2` support and nightly-native `Allocator` support should not blur together.
5. **Prefer attachable evidence over benchmark slogans.** OOM, reset, teardown, and growth vectors matter more than “faster allocator” claims.
6. **Do not flatten memory-management diversity.** Pools, slabs, arenas, bump allocators, fixed-capacity structures, and process-global allocators should remain visibly different.

## Why existing projects are not enough
The point projects are real, but they leave a coordination gap:
- std exposes primitives, not a review contract,
- `allocator-api2` mirrors unstable APIs, not a release/report format,
- bump and arena crates publish semantics, but each in their own vocabulary,
- global allocator wrappers optimize one lane only,
- and footprint/profiling tools do not describe semantic resource behavior by themselves.

The ecosystem therefore still lacks a common answer to “what exactly does this crate promise about allocation and reclamation, and how do we know?”

## Likely first users
- parser/compiler crates with arena-backed ASTs,
- graph/data-structure crates using arena/id models,
- allocator-aware collection crates,
- embedded / `no_std` code that needs explicit failure posture,
- server-side code choosing process-global allocators or pooled strategies,
- library teams that want to prove low-allocation or reset-based semantics honestly.

## Risks
- **Too unstable:** allocator-generic std APIs are still nightly.
  - Response: keep the contract lane-aware and artifact-first, with explicit stable/nightly posture.
- **Too broad:** allocation spans many design styles.
  - Response: focus on public support truth, not one implementation.
- **Too much ceremony:** systems crates may resist more metadata.
  - Response: start with auto-inspection, adapters, and a small MVP.
- **Benchmark theater:** people may try to turn the kit into a benchmark ranking.
  - Response: bias toward semantic vectors and attach performance evidence only as optional raw attachments.

## Phased plan
### Phase 1: representation
- finalize schemas,
- implement scaffold/inspect/export,
- ship adapters for global, allocator-generic, bump/arena, and id-arena lanes.

### Phase 2: checking
- add OOM/reset/drop/interop vectors,
- emit `allocation-check-report/v0`,
- add diff support for semantic regressions.

### Phase 3: ecosystem composition
- integrate with Footprint Kit, Initialization Surface Kit, Pointer Surface Kit, Validity Surface Kit, and Override Surface Kit,
- let downstream crates attach `allocation-pack/v0` in release and CI flows,
- add archaeology/migration support for allocator-lane changes.

## Interaction with the rest of this archive
This proposal should stay distinct from:
- **Override Surface Kit** — that kit owns global provider-slot installation; this kit owns the resulting memory-resource semantics.
- **Initialization Surface Kit** — initialization owns staged construction and teardown timing; this kit owns resource and reclamation semantics.
- **Footprint Kit** — footprint owns measured budget evidence; this kit owns semantic allocation claims and can attach measurements.
- **Pointer Surface Kit** — pointer semantics overlap, but allocation resources are not the same thing as pointer receiver/reborrow truth.
- **Validity Surface Kit** — validity owns invalid-value/layout assumptions; allocation surfaces own storage and reclamation truth.

## Bottom line
A genuinely worthy Rust contribution here would be:

> **Allocation Surface Kit** — one reviewable boundary for allocators, arenas, pools, OOM/failure posture, reclamation/reset semantics, stable/nightly interop lanes, and evidence across std/global allocators, allocator-generic collections, `allocator-api2`, bump/arena crates, and future memory-resource surfaces.

That would be “epic” not because it replaces today’s projects, but because it could make the whole Rust memory-resource story far easier to publish, compare, verify, and build on.
