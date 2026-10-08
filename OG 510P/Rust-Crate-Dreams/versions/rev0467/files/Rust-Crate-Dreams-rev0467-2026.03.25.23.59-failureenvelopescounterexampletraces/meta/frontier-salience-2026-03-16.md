
# Frontier salience scan — 2026-03-16

This pass again chose **not** to add another narrow top-level proposal.

The better move was to re-rank the broad portfolio using fresh 2026 signals and then upgrade two underbuilt proposals whose timing has improved:

- **P-0458 Async Dyn Transition Kit**
- **P-0465 BorrowSanitizer Workflow & Evidence Kit**

## Main judgment

The archive’s strongest next moves are still mostly **coordination artifacts above real substrate**.
But the current portfolio should now give more weight to crates that help maintainers survive **active Rust transitions** without folklore.

Three current pressures matter especially:

1. the 2025 State of Rust survey still says **resource usage** remains a major pain and **debugging** remains a top-tier pain point,
2. the 2026 Rust flagships explicitly include **Just Add Async** work such as `async fn in dyn trait`,
3. and Rust’s safety/tooling direction now includes both broader sanitizer support and BorrowSanitizer-era aliasing instrumentation.

That combination makes workflow crates for **transition truth**, **evidence truth**, and **support truth** look stronger than one more clever library in a crowded category.

## External signals worth honoring

- The 2025 State of Rust survey says resource usage is still a major non-trivial problem and that debugging, while slightly lower than in 2024, remains a top productivity limiter.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust’s 2026 flagships explicitly include **Just Add Async**, with milestones such as stabilizing return type notation and `async fn in dyn trait`.  
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2026 debugging survey explicitly calls out debugger support across backends/OSes, visualizers, async debugging, and expression evaluation.  
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- BorrowSanitizer-related compiler work is explicitly aimed at practical runtime detection of aliasing violations, especially across language boundaries.  
  https://rust-lang.github.io/rust-project-goals/2025h2/codegen_retags.html
- Cargo’s build-dir work continues to show that the ecosystem is gaining more substrate, but still needs explanation and support artifacts above it.  
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0242 Reproducible Build Evidence Kit**
3. **P-0256 Evidence Bundle Core Kit**
4. **P-0485 Verification Campaign Workbench Kit**
5. **P-0264 Rust Conformance Harness Toolkit**
6. **P-0076 Local-first Sync Kit**
7. **P-0197 Text Layout & Shaping Conformance Kit**
8. **P-0458 Async Dyn Transition Kit**
9. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit**
10. **P-0486 Debuggability Support Contract Kit**
11. **P-0465 BorrowSanitizer Workflow & Evidence Kit**
12. **P-0503 Assurance Case Workbench Kit**

## Why the two risers matter now

### 1. P-0458 Async Dyn Transition Kit
This crate is no longer just a niche language-adjacent curiosity.
The official roadmap now makes `async fn in dyn trait` part of the visible 2026 async story, while real ecosystems still depend on `async-trait`, `trait-variant`, and `dynosaur` today.

That makes a **dispatch-recipe / migration-receipt** crate unusually timely.
The gap is not another bridge macro; it is the artifact that lets maintainers compare recipes and explain why they have not migrated yet.

### 2. P-0465 BorrowSanitizer Workflow & Evidence Kit
This crate remains narrower than a general sanitizer workflow, but more differentiated.
The important missing value is not just “run the tool.”
It is the **FFI-boundary-aware, provenance-violation, optional-Miri-compare bundle** another maintainer can actually review.

As BorrowSanitizer-era tooling becomes more concrete, the archive should prefer evidence contracts over vague claims that aliasing/runtime safety is “handled”.

## What the strongest epic crates have in common right now

The best proposals in this archive increasingly satisfy most of these:

1. They solve **recurrent workflow pain**, not one-off cleverness.
2. They sit above **real substrate** that already exists.
3. They emit a **receiver-facing artifact** another person can inspect.
4. They help ecosystems survive **change and drift** honestly.
5. They can ship a real **0.1** without pretending to own the whole world.

## Working rule for the next few passes

Prefer upgrades that add:

- fixture packs,
- schema contracts,
- lane-boundary notes,
- and conservative salience re-ranking,

before adding another narrow proposal.

The archive is now large enough that **better boundaries and better handoff quality** are often worth more than proposal count.
