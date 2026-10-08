# Design: Atomic Surface Kit (`cargo atomicsurf`, `atomic-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **atomic/shared-state surfaces** in Rust: plain atomic cells, read-mostly atomic publication, lock-free pointer structures, portability/fallback-backed atomic lanes, and future alternative-memory-model or kernel-facing surfaces.

This should help answer questions like:
- what ordering guarantees does this surface actually require or promise,
- which atomic widths and CAS capabilities are required on the target,
- what happens when those capabilities are missing,
- whether the surface is lock-free, wait-free in some operations, or simply “lock-free-shaped” with retry loops,
- how removed nodes or replaced values are reclaimed,
- whether the public unit is an integer/flag, an atomic pointer, or a published snapshot,
- and what evidence demonstrates these claims.

It should **not** replace the atomic crates themselves, standardize one lock-free collection framework, or pretend all memory models and reclamation techniques are equivalent.
It should make atomic surfaces reviewable.

## References (signals)
- Std’s atomic module now explicitly documents that Rust atomics follow the C++20 atomic rules (without consume), that data races are UB, that mixed-size conflicting atomic accesses are UB, and that lock-free does not imply wait-free.
  https://doc.rust-lang.org/std/sync/atomic/index.html
- Std also documents material portability differences: some targets lack 64-bit atomics, some Arm targets have only load/store without full CAS, and maximally portable code needs to be careful about width assumptions.
  https://doc.rust-lang.org/std/sync/atomic/index.html
- The Rust Reference exposes `target_has_atomic`, which is the right raw primitive for describing width/CAS availability, but today it is not lifted into reusable ecosystem artifacts.
  https://doc.rust-lang.org/reference/conditional-compilation.html#target_has_atomic
- `portable-atomic` demonstrates that portability is not binary. It supports extra widths, no-atomic / no-CAS targets, critical-section fallbacks, and other behavior-changing lanes that libraries currently expose only through crate docs and features.
  https://docs.rs/portable-atomic/latest/portable_atomic/
- `crossbeam-epoch` demonstrates that reclamation is a first-class part of the atomic surface, not an invisible implementation detail.
  https://docs.rs/crossbeam-epoch/latest/crossbeam_epoch/
- `arc-swap` demonstrates a distinct read-mostly atomic publication lane whose contract is materially different from a lock-free node graph or a simple `AtomicUsize`.
  https://docs.rs/arc-swap/latest/arc_swap/
- Loom demonstrates that concurrency evidence needs adversarial schedule/memory-model exploration rather than only ordinary tests.
  https://docs.rs/loom/latest/loom/
- The Rust-for-Linux smart-pointer RFC explicitly says some kernel atomics need to match the Linux Kernel Memory Model rather than the ordinary LLVM/C++ atomics path.
  https://rust-lang.github.io/rfcs/3621-derive-smart-pointer.html
- Rust’s 2026 safety-critical research says ecosystem support thins out in higher-criticality environments and specifically names atomics among the core building blocks people want in evidence-friendly stacks.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

## Core design principle
The kit should model **public atomic truth, not implementation mystique**.

That means separating:
- ordering semantics,
- target capability requirements,
- progress claims,
- reclamation strategy,
- public shared-state shape,
- fallback behavior,
- and verification evidence.

Those often get blurred together in docs today, but they are different review questions and need different artifacts.

## Artifact family

### 1) `atomic-surface/v0`
Top-level identity for an atomic/shared-state surface.

Fields:
- surface id
- crate/module/item scope
- public state family (`flag`, `counter`, `cell`, `ptr-graph`, `snapshot-publish`, `hybrid`)
- intended deployment lane (`std`, `no_std`, embedded, kernel-ish, mixed)
- stability/channel posture
- summary of public guarantees and sharp edges

Design rule: this is the index card, not the full truth.

### 2) `ordering-profile/v0`
Describes the public ordering contract.

Fields:
- operations exposed (`load`, `store`, `swap`, `compare_exchange`, `fetch_*`, fences)
- orderings required / permitted / abstracted away
- success vs failure ordering posture for CAS
- whether callers choose orderings or the API fixes them
- hidden internal orderings that materially affect semantics
- atomic/non-atomic access caveats if public
- mixed-size / aliasing / transmute hazards if relevant
- memory-model notes (`C++20-style`, `LKMM-sensitive`, etc.)

Design rule: keep “which ordering exists in the code” separate from “which ordering is part of the public contract”.

### 3) `target-atomic-profile/v0`
Describes target capability and fallback posture.

Fields:
- required atomic widths (`8/16/32/64/128/ptr`)
- CAS required or optional
- `target_has_atomic` gates
- `std` / `core` / `no_std` posture
- target families with special handling
- fallback selection rules
- compile-fail vs runtime fallback vs alternate algorithm behavior
- feature flags / cfgs / MSRV interactions if relevant

Design rule: portability truth must be explicit and machine-readable.

### 4) `progress-reclamation-profile/v0`
Describes liveness and destruction posture.

Fields:
- progress claims (`lock-free`, `wait-free` for specific ops, retry-loop-only, no formal claim)
- contention expectations
- reclamation strategy (`refcount`, `epoch`, `hazard-like`, `quiescent`, `manual`, `lock-backed fallback`)
- participant registration / pinning / quiescence requirements
- remove-versus-destroy timing
- ABA posture and mitigations if public
- leak / deferred-drop / destructor timing caveats

Design rule: “lock-free” is not enough. Reclamation and destruction timing are part of the public truth.

### 5) `shared-state-profile/v0`
Describes the public shape of the state.

Fields:
- state unit (scalar cell, pointer, published snapshot, graph node, generation pair, etc.)
- ownership model
- mutation / publish / replace / remove operations
- reader guarantees
- writer guarantees
- read-mostly / write-heavy assumptions
- snapshot consistency or eventuality posture
- FFI/kernel/shared-memory notes if relevant

Design rule: keep state-shape truth separate from ordering and portability.

### 6) `atomic-adapter-profile/v0`
Describes conversions and migration bridges.

Fields:
- source and target surface ids
- conversion style (`wrap`, `fallback`, `replace`, `shim`, `ffi bridge`)
- semantic losses or gains
- allocation / refcount / lock costs if relevant
- target restrictions
- migration notes

Design rule: adapters are first-class review objects; do not bury them in changelogs.

### 7) `atomic-vector-set/v0`
Portable review vectors.

Kinds of vectors:
- ordering vector
- mixed-width / alias hazard vector
- target-width gating vector
- no-CAS / fallback vector
- publication-consistency vector
- reclamation/destruction vector
- ABA/regression vector
- loom/model vector

Each vector should record:
- vector id
- purpose
- relevant targets/features/tools
- expected behavior
- severity if it fails

Design rule: vectors are there to make surface claims testable, not to replace full proofs or performance investigations.

### 8) `atomic-check-report/v0`
Attachable evidence artifact.

Fields:
- targets/features checked
- vectors run / skipped
- Loom or equivalent runs
- fallback paths exercised
- reclamation lanes exercised
- notes on failures / caveats / unsupported lanes
- channel/MSRV/toolchain used
- raw attachments (logs, traces, cfg dumps)

### 9) `atomic-pack/v0`
Bundle containing the surface, profiles, vectors, report, docs links, migration notes, and archaeology.

## CLI shape
- `cargo atomicsurf init` — create a starter pack for a crate/module
- `cargo atomicsurf check` — run declared vectors on selected targets/tools
- `cargo atomicsurf diff` — compare packs across releases or target sets
- `cargo atomicsurf explain` — show ordering, target, progress, and reclamation posture in plain language
- `cargo atomicsurf pack` — emit an attachable artifact bundle

## Review questions this makes possible
1. Does this API really need full CAS, or only load/store on the public path?
2. Which atomic widths and target gates are part of the support contract?
3. Is this surface read-mostly snapshot publication, or a pointer-graph lock-free structure with reclamation obligations?
4. Are “lock-free” claims backed by explicit progress/reclamation notes, or only by absence of a mutex type?
5. What happens on no-CAS or no-128-bit targets?
6. Did the project actually run Loom or equivalent evidence on the documented ordering contract?
7. Can a safety-sensitive or embedded team replace this lane cleanly if they need a different fallback or memory model?

## Example v0 rollout

### Pilot A: std atomic cell / counter lane
Use a crate exposing counters, flags, or once/state cells.

Artifacts should make explicit:
- public operations and fixed orderings,
- width/CAS assumptions,
- and whether fallback exists at all.

### Pilot B: read-mostly snapshot publication lane
Use an `arc-swap`-style surface.

Artifacts should make explicit:
- snapshot consistency expectations,
- publish/replace semantics,
- refcount/destruction timing,
- and read-mostly tuning assumptions.

### Pilot C: lock-free collection / pointer lane
Use a `crossbeam-epoch`-style or equivalent surface.

Artifacts should make explicit:
- atomic pointer posture,
- epoch/pin requirements,
- remove-vs-destroy timing,
- and Loom/model evidence.

### Pilot D: portability / embedded lane
Use a `portable-atomic`-backed surface or a crate that depends on it.

Artifacts should make explicit:
- width/CAS gaps,
- fallback behavior,
- critical-section assumptions,
- and `no_std`/MSRV notes.

### Pilot E: alternative-memory-model exploratory lane
If practical, model a kernel-facing or FFI-sensitive surface where the ordinary C++20/LLVM assumptions are not the whole story.

Artifacts should make explicit:
- that the surface is exceptional,
- which memory-model notes apply,
- and where adapter boundaries to ordinary userland Rust live.

## What success looks like
The kit is working if Rust teams can answer, from one small artifact bundle:
- what kind of atomic surface they are consuming,
- which orderings and target widths matter,
- what fallback or replacement story exists,
- how progress and destruction are expected to behave,
- and what evidence actually backs the claims.

That would count as a real ecosystem contribution because it reduces review cost and replacement risk **before** teams are forced to reverse-engineer atomic assumptions from source, benchmarks, and folklore.
