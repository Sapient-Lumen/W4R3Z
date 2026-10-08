# Gap: allocation surfaces, allocators, arenas, pools, and reviewable memory-resource contracts

## What is missing
Rust has **real allocation diversity**, but the ecosystem still lacks a **portable way to describe what an allocation surface actually promises**.

Today there is no standard way to say:
- whether a crate depends on the process-global allocator, an injected allocator handle, a region/arena, a slab/pool, fixed-capacity storage, or some mixture,
- whether allocation failure aborts, returns an error, bubbles through `try_` APIs, or only exists on one code path,
- whether memory is reclaimed per object, per region reset, per generation/checkpoint, or all at once at arena teardown,
- whether resetting a region runs `Drop`, skips destructors, or requires separate ownership wrappers,
- whether allocations are thread-local, thread-safe, shareable across containers, or tied to one borrowing scope,
- which collections or pointer types can actually use the chosen memory resource on stable Rust, nightly `allocator_api`, or `allocator-api2`,
- what instrumentation or limits exist: allocation counters, byte caps, peak-watermark tracking, chunk geometry, or fragmentation-related caveats,
- and what evidence checked the claims: OOM vectors, reset/drop vectors, capacity/reallocation vectors, arena-lifetime vectors, or perf/footprint attachments.

That gap matters because Rust already has meaningful point solutions:
- std exposes a process-global allocator lane and an experimental generic `Allocator` trait,
- std collections and pointer types increasingly have `new_in` / `try_*_in` style APIs, but they remain nightly under `allocator_api`,
- `allocator-api2` exists specifically to mirror that unstable API on stable Rust,
- `hashbrown` and other crates already bridge into `allocator-api2`,
- `bumpalo` exposes bump/arena allocation with collection support and reset semantics,
- arena crates publish bulk-teardown or id-based lifetime models,
- and global allocator wrappers like `mimalloc` still represent a distinct process-wide lane.

So the missing contribution is not one magical allocator crate.
It is a **reviewable allocation-surface layer** for publishing allocator/resource identity, failure posture, reclamation semantics, stable/nightly interop, and evidence honestly.

Sources:
- https://doc.rust-lang.org/std/alloc/trait.Allocator.html
- https://doc.rust-lang.org/std/alloc/index.html
- https://doc.rust-lang.org/std/vec/struct.Vec.html
- https://doc.rust-lang.org/beta/alloc/boxed/struct.Box.html
- https://docs.rs/allocator-api2
- https://docs.rs/hashbrown
- https://docs.rs/bumpalo
- https://docs.rs/typed-arena/
- https://docs.rs/mimalloc
- https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## The current seam is awkward
Rust already spans several materially different memory-resource shapes, but today most of that truth is split across nightly docs, crate README text, and folklore:
- std’s `Allocator` trait remains experimental, even though it already defines allocate/grow/shrink/deallocate semantics for arbitrary `Layout`s,
- std `Box`, `Vec`, `HashSet`, `LinkedList`, `Rc`, and related APIs expose `*_in` constructors on nightly, which is evidence that allocator-parameterized collections are real but not yet a boring stable default,
- `allocator-api2` exists precisely because the ecosystem still wants allocator-generic code on stable Rust,
- `hashbrown` treats `allocator-api2` support as a real feature lane,
- `bumpalo` exposes a distinct region model with optional `allocator-api2` integration and reset behavior that does not run destructors,
- typed/graph arena families expose still-different models centered on bulk teardown or id-based access rather than general allocation interfaces,
- and process-global allocator wrappers keep the override lane alive because many users still want a single allocator choice for the whole process.

These are not minor implementation details.
They determine latency spikes, fragmentation risk, reset safety, destructor behavior, OOM handling, portability across stable/nightly, and whether downstream users can compose containers and memory resources honestly.

Sources:
- https://doc.rust-lang.org/std/alloc/trait.Allocator.html
- https://doc.rust-lang.org/std/vec/struct.Vec.html
- https://doc.rust-lang.org/beta/alloc/boxed/struct.Box.html
- https://docs.rs/allocator-api2
- https://docs.rs/hashbrown
- https://docs.rs/bumpalo
- https://docs.rs/typed-arena/
- https://docs.rs/mimalloc

## Why this matters
This gap matters because allocation choices cut across several important Rust futures at once:
1. **performance and footprint** — allocator/resource choices affect latency, fragmentation, cache behavior, and peak memory shape.
2. **correctness and teardown** — region reset, bulk free, and `Drop` behavior are public semantic differences.
3. **embedded / constrained / safety-critical work** — failure posture and fixed-capacity or pooled allocation strategies matter more than “just abort on OOM”.
4. **library composability** — stable/nightly allocator-generic APIs, arenas, and process-global allocators are all real but poorly compared.
5. **tooling honesty** — “low allocation” or “arena-backed” claims are not very useful unless reset/reclamation and interop limits are explicit.

A worthy contribution here is therefore not another allocator benchmark bake-off.
It is a way to treat allocation surfaces as **reviewable ecosystem infrastructure**.

Sources:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/std/alloc/trait.Allocator.html
- https://docs.rs/bumpalo
- https://docs.rs/typed-arena/
- https://rust-lang.github.io/rfcs/2116-alloc-me-maybe.html

## What “good” looks like
A worthy contribution here is **not** one universal allocator abstraction that erases meaningful differences.

It is a shared allocation-surface boundary:
- one `allocation-surface/v0` describing the top-level surface identity, intended workloads, and whether the package is global-allocator-centric, allocator-generic, arena/region-based, pool/slab-based, fixed-capacity, or mixed,
- one `memory-resource-profile/v0` for resource identity, ownership model, thread-safety/shareability, byte-limit/chunking posture, and stable/nightly API lane,
- one `container-allocation-profile/v0` for which containers/pointers/resources compose, when reallocation happens, and what growth/shrink/zeroed/uninit/fallible operations are exposed,
- one `region-lifetime-profile/v0` for region reset/checkpoint/generation semantics, destructor behavior, and reference/id invalidation timing,
- one `oom-failure-profile/v0` for abort/error/panic/none posture, `try_` coverage, and fallback policy,
- one `allocation-adapter-profile/v0` for bridges between nightly `Allocator`, `allocator-api2`, global-allocator wrappers, bump arenas, typed/id arenas, and fixed-capacity lanes,
- one `allocation-vector-set/v0` for OOM, reset/drop, growth/reallocation, and stable/nightly interop vectors,
- one `allocation-check-report/v0` recording which vectors actually ran on which targets/channels,
- and one `allocation-pack/v0` bundle for docs, CI, migration notes, and archaeology.

That would let Rust teams review “allocator-aware” or “arena-backed” claims using explicit artifacts instead of guessing from README prose, benchmark charts, or hidden feature flags.

## Non-goals
This gap should not be used to:
- define all memory management in Rust,
- replace std allocators, `allocator-api2`, bump allocators, arena crates, or global allocator wrappers,
- flatten process-global allocators, allocator-generic containers, region allocation, id arenas, and fixed-capacity structures into one fake universal memory model,
- or turn allocator selection into a shallow benchmark leaderboard.

The job is smaller and sharper:
**make allocation surfaces legible, honest, and checkable across allocators, arenas, pools, failure lanes, and evidence.**
