# Design: Allocation Surface Kit (`cargo allocsurf`, `allocation-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **allocation surfaces** in Rust: process-global allocators, allocator-generic collections/pointers, arenas/regions, slabs/pools, id arenas, and mixed allocation strategies.

This should help answer questions like:
- what memory resource model a crate actually uses,
- whether allocation failure aborts, panics, or returns an error,
- which containers and pointer types genuinely compose with that resource,
- how reset/bulk-free/teardown behave,
- whether destructors run when memory is reclaimed,
- what stable/nightly/API-lane assumptions apply,
- and what evidence shows the claimed semantics are real.

It should **not** replace allocators or arena crates themselves, standardize one allocator implementation, or force all memory-management styles into one common denominator.

## Why now
This seam has become strategically relevant because Rust now spans several real but poorly aligned allocation shapes at once:
- std still exposes a process-global allocator model,
- std’s generic `Allocator` trait and `*_in` APIs remain experimental even though they already cover real collections and pointer types,
- stable Rust users reach for `allocator-api2` specifically because the ecosystem wants allocator-generic code now,
- containers such as `hashbrown` already carry allocator-generic support on stable,
- region/bump allocators and arena crates remain common in parsers, compilers, and graph-heavy code,
- and high-level crates still need a way to describe low-allocation / arena-backed / pooled behavior honestly.

That is exactly the moment when an **allocation-surface contract** becomes more valuable than one more allocator benchmark or one more specialized pool crate.

## Design principles
1. **Do not lie about the memory resource.** Process-global allocators, injected allocators, arenas, pools, and fixed-capacity storage are not interchangeable.
2. **Do not lie about failure posture.** Abort, panic, and recoverable allocation failure are materially different public behaviors.
3. **Keep reclamation semantics first-class.** Per-object free, region reset, checkpoint rollback, and bulk teardown must stay visible.
4. **Keep destructor behavior first-class.** “Memory reclaimed” is not the same thing as “`Drop` ran”.
5. **Keep stable/nightly interop first-class.** Native nightly `Allocator`, `allocator-api2`, and global-allocator-only lanes must remain visibly different.
6. **Prefer attachable evidence over prose promises.** OOM vectors, reset/drop vectors, and interop checks matter more than README adjectives.

## Artifact family
### `allocation-surface/v0`
Top-level declaration for a crate or package.

Fields should include:
- package/crate identity
- allocation family (`global-allocator`, `allocator-generic`, `arena-region`, `pool-slab`, `id-arena`, `fixed-capacity`, `mixed`, `other`)
- intended workloads
- stable/nightly/MSRV posture
- target/`no_std` posture
- attached subprofiles

### `memory-resource-profile/v0`
Describe the memory resource itself.

Fields should include:
- resource kind (`global`, `system`, `custom-allocator`, `bump`, `arena`, `slab`, `pool`, `fixed-capacity`, `other`)
- ownership model (`process-global`, `owned-handle`, `borrowed-handle`, `shared-handle`, `scoped`, `other`)
- thread-safety/shareability posture
- chunking/growth strategy
- byte-limit or accounting support
- statistics/instrumentation availability
- stable/nightly/API-lane support (`std::alloc::Allocator`, `allocator-api2`, custom-only, etc.)

### `container-allocation-profile/v0`
Describe how containers and pointer types interact with the resource.

Fields should include:
- supported containers/pointers
- allocation / reallocation / shrink posture
- uninit/zeroed/fallible constructor support
- zero-sized-type behavior if noteworthy
- ownership/borrowing caveats
- raw-pointer or unsafe round-trip APIs if public

### `region-lifetime-profile/v0`
Describe region/arena/pool lifetime semantics.

Fields should include:
- allocation scope / generation / checkpoint model
- reset semantics
- whether `Drop` runs on reset / teardown / explicit wrapper only
- invalidation timing for references, ids, or handles
- leak/forget caveats
- thread/borrow restrictions

### `oom-failure-profile/v0`
Describe failure posture.

Fields should include:
- default OOM behavior (`abort`, `panic`, `error`, `none`, `mixed`)
- `try_` coverage / fallible API coverage
- fallback policy
- target-specific notes
- policy knobs / limits

### `allocation-adapter-profile/v0`
Describe bridges between allocation lanes.

Fields should include:
- source and destination lane
- conversion or wrapper model
- hidden costs (boxing, indirection, lost reset semantics, lost thread-safety, feature gating)
- channel requirements (stable/nightly)
- behavioral changes (`Drop`, OOM, capacity growth, stats visibility)

### `allocation-vector-set/v0`
Reviewable tests and examples.

Vector classes should include:
- recoverable-OOM vectors
- abort/panic expectation vectors
- growth/shrink/reallocation vectors
- arena reset / checkpoint / teardown vectors
- destructor-behavior vectors
- stable/nightly interop vectors

### `allocation-check-report/v0`
Record what actually ran.

Fields should include:
- toolchain/channel
- target triple
- enabled features
- vector ids and verdicts
- known gaps / skipped lanes
- attached raw artifacts or benchmark/footprint references when available

### `allocation-pack/v0`
Bundle the artifacts for release, CI, or archaeology.

## CLI shape
A plausible MVP command would be:

```text
cargo allocsurf [check|diff|export]
```

Possible behaviors:
- inspect a workspace for likely allocation lanes,
- scaffold profile files,
- run bounded vectors,
- diff allocation-surface changes across releases,
- export one portable `allocation-pack/v0`.

## Example use cases
### A) Drop-in global allocator wrapper
Publish:
- `allocation-surface/v0` saying process-global lane
- `memory-resource-profile/v0` for the allocator wrapper
- `oom-failure-profile/v0` documenting global behavior assumptions
- optional benchmark/footprint attachments

### B) Allocator-generic collection crate
Publish:
- allocator-generic top-level surface
- container-allocation profiles for each public collection
- adapter profile for nightly `Allocator` and stable `allocator-api2`
- stable/nightly vector coverage

### C) Bump/arena parser or compiler crate
Publish:
- arena-region top-level surface
- region lifetime profile covering reset and checkpoint semantics
- destructor-behavior vectors
- adapter notes for arena-backed collections

### D) Id-arena / graph crate
Publish:
- id-arena or mixed top-level surface
- invalidation timing for ids/handles
- explicit bulk-teardown posture
- allocation/failure semantics for growth

## Why this is better than today
Today, downstream users infer memory behavior from vague phrases like “low allocation”, “arena backed”, “uses the system allocator”, or “supports custom allocators”.
Those phrases hide the most important questions:
- is the allocator process-global or injected,
- what actually happens on allocation failure,
- whether destructors run on reset,
- whether stable Rust can use the API,
- and what evidence actually checked those claims.

Allocation Surface Kit makes those questions first-class without requiring the ecosystem to converge on one allocator implementation.

## Boundaries with nearby kits
- **Not Override Surface Kit:** that kit owns installation and lifecycle of process-global provider slots like `#[global_allocator]`; Allocation Surface Kit owns public resource semantics once a lane is chosen.
- **Not Initialization Surface Kit:** that kit owns placement, partial assembly, and teardown timing of values; Allocation Surface Kit owns the memory-resource and reclamation lane underneath.
- **Not Footprint Kit:** that kit owns measured size/stack/heap evidence; Allocation Surface Kit owns semantic allocation contracts and can attach footprint data as evidence.
- **Not Pointer Surface Kit:** pointer semantics matter here, but this kit is about memory-resource choice and reclamation behavior, not receiver/projection/dyn posture.
- **Not Validity Surface Kit:** validity owns byte/layout/invalid-value assumptions; Allocation Surface Kit owns how memory is obtained, reused, and reclaimed.

## Non-goals
- No attempt to define one universal allocator trait beyond what Rust and crates already expose.
- No attempt to replace `allocator-api2`, `bumpalo`, arena crates, or global allocator wrappers.
- No attempt to reduce allocator choice to benchmark charts.
- No attempt to hide meaningful differences in `Drop`, OOM, or scope semantics.

## MVP shape
The first practical MVP should target four lanes:
1. process-global allocator wrappers,
2. allocator-generic collection crates,
3. bump/arena crates,
4. one id-arena or graph-arena family.

That MVP would already be enough to prove whether one reviewable artifact family can sit above today’s fragmented Rust allocation ecosystem without flattening it.
