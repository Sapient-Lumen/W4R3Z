# Gap: Async lifecycle correctness and runtime portability are still too ad hoc

## Summary
Rust is making real progress on async language ergonomics, but the ecosystem still lacks a **small, portable lifecycle layer** that makes task ownership, cancellation, graceful shutdown, and runtime portability reviewable in ordinary library and service code.

Today, most teams assemble this story out of runtime-specific pieces: Tokio `CancellationToken`, `TaskTracker`, `JoinSet`, tracing spans, local shutdown conventions, and bespoke test helpers. That is good enough for experts, but it is not yet a standard, attachable, reusable ecosystem contract.

## Why now
- Async remains an explicit multi-year Rust priority. The 2025H1 async flagship says async should feel as expressive, reliable, and productive as sync Rust, and calls out runtime choice, runtime interoperability, cancellation sharp edges, and reliability as central pain points.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- The May 2025 project-goals update says current language work is intended to unblock the **next generation of async libraries**, and notes new official Async Book chapters on concurrency primitives, structured concurrency, and pinning.
  https://blog.rust-lang.org/2025/06/20/may-project-goals-update/
- The 2026 flagship themes keep **Just Add Async** alive: patterns that work in sync Rust should work in async Rust, with milestones including return type notation, `async fn` in `dyn Trait`, immobile types / guaranteed destructors, and ergonomic ref-counting.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Pin ergonomics is still active work because async and generators depend on immobility and today’s pinning story is still awkward enough to block broader library and tooling convergence.
  https://rust-lang.github.io/rust-project-goals/2025h2/pin-ergonomics.html
- Ergonomic ref-counting is explicitly motivated by async programs that share context across multiple tasks, which is a reminder that the friction is not only language syntax; it is also lifecycle structure and task ownership.
  https://rust-lang.github.io/rust-project-goals/2025h2/ergonomic-rc.html
- Tokio already documents a workable graceful-shutdown recipe built from `CancellationToken`, task tracking, and wait-for-drain patterns, which shows the pieces are real even though the contract is still runtime-specific.
  https://tokio.rs/tokio/topics/shutdown

## Concrete missing pieces
1. **Portable lifecycle primitives**
   - tracked or scoped spawning
   - cancellation propagation
   - graceful shutdown waiting
   - explicit drop policy for task groups
2. **Structured concurrency defaults**
   - discourage detached tasks by default
   - make shutdown trees visible and auditable
   - attach budgets and reason codes to drain behavior
3. **Runtime-portable library ergonomics**
   - enough common surface for libraries to avoid exploding runtime feature matrices
   - runtime adapters with explicit capability gaps instead of fake interchangeability
4. **Diagnostics and evidence**
   - task-topology reports
   - shutdown / cancellation-path reports
   - reduced repro packs for hangs, leaks, and cancellation hazards
5. **CI-facing checks**
   - no untracked tasks in declared scopes
   - shutdown drained within declared policy budget
   - cancellation path exercised in tests

## Desired properties
- Runtime-agnostic core, runtime-specific adapters.
- Small enough to complement upstream async evolution instead of replacing runtimes.
- Explicit semantics around cancellation, joining, detaching, and drop.
- Integrates with tracing, Replay Kit, and Debugger Experience Kit rather than duplicating them.
- Starts as crates plus a cargo-side doctor/report tool and a ranked pilot program.

## Distinction from nearby archive entries
- **Replay Kit** is about deterministic reproduction and minimized bug cassettes for async/concurrency failures.
- **Async Lifecycle Kit** is about making ordinary task ownership, cancellation, and shutdown more correct and reviewable *before* debugging begins.
- **Debugger Experience Kit** is about portable debugger capability claims; it can consume async topology/cancellation evidence but is not the source of that evidence.
- **Background Work Kit** is about durable job/workflow semantics, not the lower-level lifecycle substrate shared by services and libraries.
