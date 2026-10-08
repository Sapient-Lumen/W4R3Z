# Gap: atomic surfaces, ordering contracts, and reviewable progress/reclamation truth

## What is missing
Rust has meaningful atomic building blocks, but the ecosystem still lacks a **portable way to describe what an atomic/shared-state surface actually promises**.

Today there is no standard way to say:
- which memory orderings a public API requires, permits, or deliberately hides,
- whether a surface depends on compare-and-swap, wider-than-pointer atomics, fences, atomic pointers, or only load/store,
- which atomic widths are required on the target and which widths are optional acceleration,
- whether unsupported targets fail to compile, use a global-lock fallback, use interrupt-masking / critical-section tricks, or switch to a different algorithm,
- whether the surface is merely lock-free, aims for wait-freedom on some operations, or silently spins with compare-and-swap retry loops,
- how removed nodes, snapshots, or replaced values are reclaimed: reference counting, epochs, hazard-style protection, quiescent-state assumptions, or something else,
- whether the public surface is a flag/counter cell, an atomic pointer graph, an `Arc` snapshot/publish lane, or an intrusive lock-free structure,
- and which claims were actually checked with Loom/model tests, target-width gating tests, fallback-path tests, or architecture-specific runs.

That gap matters because Rust atomics are semantically sharp:
- the standard library says Rust atomics follow the C++20 atomic rules (minus consume), with mixed-size conflicting atomic accesses remaining UB,
- standard atomics are only available on targets with the relevant `target_has_atomic` width,
- some targets still lack full CAS support,
- `portable-atomic` exists because users need portable integer/float/128-bit atomics and fallbacks beyond what std offers,
- `crossbeam-epoch` exists because memory reclamation is a first-class problem for lock-free collections,
- `arc-swap` exists because read-mostly atomic publication is a real and different design lane,
- Loom exists because atomic correctness depends on executions users do not usually see in ordinary tests,
- and the Rust-for-Linux work explicitly says some kernel use-cases cannot just inherit the ordinary LLVM/C++ atomics story.

So the missing contribution is not one more atomic wrapper.
It is a **reviewable atomic-surface layer** for publishing ordering assumptions, target requirements, progress/reclamation posture, and evidence honestly.

Sources:
- https://doc.rust-lang.org/std/sync/atomic/index.html
- https://doc.rust-lang.org/reference/conditional-compilation.html#target_has_atomic
- https://docs.rs/portable-atomic/latest/portable_atomic/
- https://docs.rs/crossbeam-epoch/latest/crossbeam_epoch/
- https://docs.rs/arc-swap/latest/arc_swap/
- https://docs.rs/loom/latest/loom/
- https://rust-lang.github.io/rfcs/3621-derive-smart-pointer.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

## The current seam is awkward
Rust already has real and meaningful diversity in atomic/shared-state strategy, but most of it is published as scattered docs, cargo features, or folklore:
- std documents the core memory-model truth: Rust currently follows the C++20 atomic rules, data races are UB, conflicting mixed-size atomic accesses are also UB, and atomic operations may be lock-free without being wait-free;
- std also documents material portability differences, including targets without some widths and Arm M-profile targets with load/store but not full CAS support;
- the Rust Reference exposes `target_has_atomic`, but most crates still do not publish their atomic-width expectations in a reusable artifact;
- `portable-atomic` explicitly adds multiple portability lanes: larger atomics, no-atomic and no-CAS support, global-lock fallbacks, and critical-section-based fallbacks;
- `crossbeam-epoch` publishes a very different truth: reclamation is epoch-based and tied to pin/unpin participation;
- `arc-swap` publishes a read-mostly snapshot lane where the atomic unit is effectively an `Arc`-backed published view rather than a low-level integer cell or lock-free node graph;
- Loom tests under the C11 model, which is excellent evidence that the real semantic surface is not just “uses atomics”, but “uses atomics with specific ordering assumptions that survive adversarial interleavings”;
- and the smart-pointer RFC motivated by Rust-for-Linux explicitly says some kernel use-cases need atomics that match the Linux Kernel Memory Model rather than the ordinary LLVM/C++ path.

Those are not minor implementation details. They determine whether a library works on embedded/no-std targets, whether swapping in a different target or runtime changes correctness assumptions, whether a downstream crate can expose the type publicly, and whether a “lock-free” claim is about algorithm structure, progress properties, or just marketing.

Sources:
- https://doc.rust-lang.org/std/sync/atomic/index.html
- https://doc.rust-lang.org/reference/conditional-compilation.html#target_has_atomic
- https://docs.rs/portable-atomic/latest/portable_atomic/
- https://docs.rs/crossbeam-epoch/latest/crossbeam_epoch/
- https://docs.rs/arc-swap/latest/arc_swap/
- https://docs.rs/loom/latest/loom/
- https://rust-lang.github.io/rfcs/3621-derive-smart-pointer.html

## Why this matters
This gap matters because atomic/shared-state choices cut across several important Rust futures at once:
1. **concurrency correctness** — ordering mistakes and reclamation mistakes are among the hardest bugs to review from prose alone.
2. **portability** — target atomic width and CAS support are part of whether a crate is actually deployable on embedded, legacy, or safety-sensitive targets.
3. **evidence quality** — Loom/model checks, target-gating checks, and fallback-path tests are not optional polish when the semantic surface is adversarial interleavings.
4. **public API honesty** — a counter/flag API, an `Arc` snapshot API, and a lock-free pointer-graph API are all “atomic”, but they promise very different things.
5. **ecosystem evolution** — if Rust wants more safety-critical and platform-diverse adoption, atomic assumptions must become easier to explain, review, and replace.

A worthy contribution here is therefore not another lock-free collection or another portable-atomic shim.
It is a way to treat atomic/shared-state surfaces as **reviewable ecosystem infrastructure**.

Sources:
- https://doc.rust-lang.org/std/sync/atomic/index.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://docs.rs/loom/latest/loom/
- https://docs.rs/portable-atomic/latest/portable_atomic/

## What “good” looks like
A worthy contribution here is **not** one universal atomic abstraction that erases meaningful differences.

It is a shared atomic-surface boundary:
- one `atomic-surface/v0` describing the top-level identity, intended deployment lane, and whether the surface is cell-like, pointer-graph-like, snapshot/publish, or fallback-backed,
- one `ordering-profile/v0` for the public ordering contract, hidden internal orderings, fences, failure-ordering posture, and mixed atomic/non-atomic caveats,
- one `target-atomic-profile/v0` for required widths, CAS expectations, `target_has_atomic` gates, `std`/`no_std` posture, and fallback selection rules,
- one `progress-reclamation-profile/v0` for lock-free/wait-free claims, retry-loop posture, contention expectations, reclamation strategy, pin/quiescence requirements, and destroy-after-remove timing,
- one `shared-state-profile/v0` for the public state shape: flags/counters, atomic cells, pointer ownership model, snapshot publication, ABA posture, and mutation rules,
- one `atomic-adapter-profile/v0` for conversions between std atomics, portable-atomic lanes, `Arc` snapshot lanes, lock-backed fallbacks, or FFI/kernel-specific atomics,
- one `atomic-vector-set/v0` for ordering, width-gating, fallback, reclamation, and read-mostly publication vectors,
- one `atomic-check-report/v0` recording which vectors actually ran on which targets/features/tools,
- and one `atomic-pack/v0` bundle for docs, CI, migration notes, and archaeology.

That would let Rust teams review atomic claims using explicit artifacts instead of inferring them from crate names, perf graphs, unsafe comments, or “it passed the tests” folklore.

## Non-goals
This gap should not be used to:
- define all concurrency in Rust,
- replace std atomics, `portable-atomic`, `crossbeam-epoch`, `arc-swap`, or Loom,
- flatten atomics, synchronization primitives, lock-free collections, and kernel-specific memory-model needs into one fake universal concurrent-state model,
- or turn progress claims into a shallow leaderboard.

The job is smaller and sharper:
**make atomic/shared-state surfaces legible, honest, and checkable across orderings, targets, reclamation strategies, and verification lanes.**
