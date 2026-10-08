# Epic proposal: Atomic Surface Kit

## Thesis
Rust already has strong atomic ingredients, but the semantic surface remains too implicit.

Std gives the core memory-model rules, `target_has_atomic` exposes target capability, `portable-atomic` fills portability gaps, `crossbeam-epoch` handles reclamation for lock-free structures, `arc-swap` gives a read-mostly atomic publication lane, and Loom gives adversarial concurrency testing.

What is still missing is a **shared review/evidence layer above those pieces**.

So the epic contribution here is not another atomic helper crate.
It is **Atomic Surface Kit**: one portable way to publish ordering contracts, target-width/CAS posture, progress/reclamation behavior, shared-state shape, and checked evidence for atomic Rust surfaces.

## Why this is worthy
This is worthy because it helps Rust in several high-value ways at once:
1. **safer concurrency design** — ordering and reclamation assumptions become explicit review objects;
2. **better portability** — target atomic widths and fallback rules become visible instead of hidden in cfgs and docs;
3. **better composition** — downstream crates can tell whether they are depending on counters, snapshots, or pointer-graph lock-free structures;
4. **better evidence** — Loom/model checks and target/fallback checks gain a stable artifact family;
5. **better adoption for platform-diverse and safety-sensitive teams** — atomic assumptions become easier to explain, constrain, replace, and audit.

## Signals
- Std atomics explicitly document the C++20-style memory model, mixed-size UB, lock-free vs wait-free distinction, and platform-specific atomic capability limits.
  https://doc.rust-lang.org/std/sync/atomic/index.html
- The Rust Reference exposes `target_has_atomic`, which is the right base primitive for machine-readable target capability declarations.
  https://doc.rust-lang.org/reference/conditional-compilation.html#target_has_atomic
- `portable-atomic` demonstrates ongoing demand for portability lanes, 128-bit atomics, float atomics, no-CAS support, and embedded fallbacks.
  https://docs.rs/portable-atomic/latest/portable_atomic/
- `crossbeam-epoch` demonstrates that reclamation is a public problem for lock-free structures, not just a private implementation detail.
  https://docs.rs/crossbeam-epoch/latest/crossbeam_epoch/
- `arc-swap` demonstrates a distinct snapshot/publication lane optimized for read-mostly workloads.
  https://docs.rs/arc-swap/latest/arc_swap/
- Loom demonstrates that ordinary testing is not enough to validate atomic correctness under adversarial interleavings.
  https://docs.rs/loom/latest/loom/
- The Rust-for-Linux smart-pointer RFC explicitly calls out atomic memory-model issues in kernel contexts, showing the atomic story is broader than one userland memory model.
  https://rust-lang.github.io/rfcs/3621-derive-smart-pointer.html
- Rust’s 2026 safety-critical research explicitly names atomics among the building blocks teams want in evidence-friendly stacks.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

## Proposed scope
Ship:
1. `atomic-surface/v0`, `ordering-profile/v0`, `target-atomic-profile/v0`, `progress-reclamation-profile/v0`, `shared-state-profile/v0`, `atomic-adapter-profile/v0`, `atomic-vector-set/v0`, `atomic-check-report/v0`, and `atomic-pack/v0`
2. `cargo atomicsurf` for init/check/diff/explain/pack workflows
3. one std-cell/counter pilot
4. one read-mostly snapshot/publication pilot
5. one lock-free collection / reclamation pilot
6. one portability / embedded fallback pilot
7. one exploratory alternative-memory-model pilot if practical

Do **not** ship:
- a universal lock-free runtime,
- a replacement for std atomics or existing crates,
- a fake “concurrency safe” badge,
- or a single benchmark score pretending to summarize the whole surface.

## Early roadmap
### v0.1 — schema + simple cell lane
- finalize artifact family
- document one counter/flag/cell surface
- prove ordering + target capability declarations can stay small and clear

### v0.2 — portability and publication lanes
- add one `portable-atomic`-backed pilot
- add one `arc-swap`-style pilot
- validate target/fallback and read-mostly snapshot publication profiles

### v0.3 — lock-free + evidence lane
- add one `crossbeam-epoch`-style pilot
- add Loom/model vectors
- ship `cargo atomicsurf explain`

### v0.4 — adapters + exceptional lanes
- add adapter profiles between std, portable, and snapshot/reclamation lanes
- model one alternative-memory-model or kernel-facing exploratory case if practical
- attach reports to CI/release notes

## What success looks like
Within a few revisions, the repo should be able to point to a credible story for:
- how Rust crates honestly publish atomic public support,
- how to compare std atomics, portability/fallback lanes, snapshot-publication lanes, and lock-free/reclamation lanes,
- how to review target capability and memory-ordering hazards,
- and how to attach evidence rather than relying on folklore.

That would count as a real ecosystem contribution because it lowers the cost of building and reviewing serious shared-state Rust without pretending the ecosystem needs one universal atomic abstraction.
