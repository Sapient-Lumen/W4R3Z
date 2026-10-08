# Frontier salience refresh — 2026-03-22 (201)

## Why this pass went broad again

The archive had just spent many passes productizing already-strong support-contract lanes.
That was good work.
But the March 2026 challenge synthesis and the latest official survey results were a reminder that the repo still needs periodic **whole-ecosystem reranks**.

The broad question for this pass was:

> Across extreme variety of use cases, what still looks missing enough — and useful enough to other people — to deserve top billing?

## Main ranked takeaway

The strongest new opening is a lane the archive had not yet named sharply enough:
**compile iteration feedback**.

Rust now has real substrate for faster local loops — faster default linking, experimental relink work, framework-local hot reload, runtime hotpatching, and mature watch-loop tools — but still lacks one receiver-facing crate that explains **what kind of live update was actually possible, what state continuity is being claimed, and what fallback restart route remains**.

That makes **P-0537 Compile Iteration Feedback Kit** a worthy addition to the top frontier.

## Current ranked frontier

### Highest

1. **P-0537 Compile Iteration Feedback Kit**
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**

### Very high

5. **P-0011 Crate Health Contract Kit**
6. **P-0121 FFI Boundary Conformance Kit**
7. **P-0532 Async Runtime Assurance Profile Kit**
8. **P-0486 Debuggability Support Contract Kit**
9. **P-0484 Toolchain & Target Support Contract Kit**

### High

10. **P-0469 Cargo Rebuild Explanation Kit**
11. **P-0035 cargo-build-insights**
12. **P-0490 Cargo Lock Contention Witness Kit**
13. **P-0433 MC/DC Coverage Workbench Kit**
14. **P-0120 Unsafe Contract Auditor Kit**
15. **P-0435 Cargo Script Workbench Kit**

## Why the new top four look strongest

### 1. P-0537 Compile Iteration Feedback Kit
Why it belongs:
- official challenge work now frames compile/iteration pain as universal;
- GUI and long-running-process workflows now have real hot-reload/hotpatch substrate;
- but the ecosystem still lacks a stable contract for patch eligibility, state continuity, and restart fallback.

### 2. P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit
Why it stays near the top:
- official challenge work explicitly highlights crate-choice tacit knowledge and choice paralysis;
- this lane helps turn that tacit knowledge into reviewable decisions rather than another blog-post canon.

### 3. P-0535 Dependency Lifecycle Transition Kit
Why it stays high:
- long-lived and safety-critical teams still need to adopt crates early, then constrain, replace, or internalize them later;
- the missing value remains a transition artifact set, not more dependency-policy prose.

### 4. P-0536 Crate Knowledge Pack Kit
Why it remains central:
- docs remain canonical,
- assistant/search usage is growing,
- and maintainers still lack a provenance-aware, compact, machine-consumable export of crate understanding.

## What this pass deprioritized slightly

This pass did **not** decide that safety-critical, debugging, or target-support lanes are unimportant.
It decided that the archive had recently given them heavy productization attention, while the broad, cross-domain iteration loop still lacked a named lane.

## Freshness anchors

- 2025 State of Rust survey — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust challenges / vision follow-up — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- Rust compiler performance survey 2025 results — https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Faster linking times with Rust 1.90 — https://blog.rust-lang.org/2025/09/01/rust-lld-on-1.90.0-stable/
- Relink don’t Rebuild goal — https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Subsecond docs — https://docs.rs/subsecond
- Dioxus hot reload docs — https://dioxuslabs.com/learn/0.7/essentials/ui/hotreload/
- Rust in 2026 flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
