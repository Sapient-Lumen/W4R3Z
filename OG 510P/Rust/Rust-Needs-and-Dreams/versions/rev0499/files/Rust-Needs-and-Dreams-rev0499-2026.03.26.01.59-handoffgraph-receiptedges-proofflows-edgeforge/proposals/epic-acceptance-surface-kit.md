# Epic Proposal: Acceptance Surface Kit (`cargo acceptsurf`)

## One-sentence pitch
Create a portable evidence layer for solver- and borrow-check-sensitive Rust patterns: name the patterns, record which compiler lanes were exercised, publish expected pass/fail/workaround posture, and attach diffable `acceptance-pack/v0` artifacts instead of relying on scattered UI tests and folklore.

## Thesis
One of the strongest missing ecosystem contributions in Rust is a **reviewable acceptance contract** for advanced patterns.

Rust is now actively changing the machinery behind trait solving and borrow checking, but most crates still communicate support with prose like “works on nightly”, “requires a workaround”, or “blocked on compiler issue X”. That is not enough. Libraries and tools need a boring, explicit way to say which patterns they intentionally support, which remain unsupported, which alternate formulations are equivalent or lossy, and what happened when those claims were checked on stable, nightly, next-solver, or Polonius lanes.

In other words: Rust needs a portable `acceptance-pack/v0` more than it needs one more local UI-test directory that only the original maintainer knows how to interpret.

## Why now
The timing is unusually good:
- 2026 flagships explicitly aim to stabilize the **next-generation trait solver** and frame lending iterators / evolvable trait hierarchies as core dormant-traits work;
- the 2025H2 next-solver goal says the new solver should replace the existing implementation, fix unsoundnesses, improve compile-times, and extend into lints and rustdoc;
- the 2025H2 Polonius goal says the nightly implementation should accept lending iterators, be stabilizable, and include debugging / dump tooling;
- the evolving-traits goal is directly about transitions like `Deref: Receiver`, `Iterator: LendingIterator`, and local/send split trait families;
- `compiletest`, `trybuild`, and `ui_test` already prove that Rust users care enough about acceptance and error behavior to invest in executable fixtures.

That means the seam is visible before it has converged.
This is exactly when an explicit evidence boundary is most valuable.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
- https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- https://rustc-dev-guide.rust-lang.org/tests/compiletest.html
- https://docs.rs/trybuild
- https://docs.rs/ui_test

## What should be built
A first credible version should ship:
1. `acceptance-subject/v0`, `pattern-catalog/v0`, `compiler-lane-profile/v0`, `acceptance-expectation-set/v0`, `workaround-profile/v0`, `acceptance-vector-set/v0`, `acceptance-check-report/v0`, `acceptance-diff-report/v0`, and `acceptance-pack/v0`
2. one trait-solver pilot comparing stable/nightly/next-solver behavior for advanced bound patterns
3. one Polonius pilot comparing stable/nightly/Polonius behavior for a lending or NLL-problem-family case
4. one trait-evolution pilot capturing local/send split and conceptual supertrait transitions
5. adapters for `trybuild`, `ui_test`, and (optionally) compiler-style UI-test fixtures
6. docs and CI that make pass/fail/workaround posture explicit without requiring readers to understand every fixture file manually

The winning version is small, semantic, and lane-aware.
It should make acceptance claims legible together rather than creating another half-hidden test harness empire.

## Initial pilots
- **Trait-solver lane** — HRTB / associated-type / opaque-return cases that currently live close to solver edges
- **Borrow-check lane** — lending and NLL-problem-family cases where Polonius may accept patterns current stable rejects
- **Trait-family lane** — local/send split traits and conceptual supertrait/subtrait evolution with explicit workaround truth
- **Public-API lane** — one crate publishes which advanced patterns are genuinely part of its supported public surface

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document lane vocabulary, pattern vocabulary, and reason classes
2. **v0.2 trait and borrow pilots**
   - ship stable/nightly/experimental-lane checks for at least two materially different pattern families
   - attach check and diff reports to real CI runs
3. **v0.3 workaround depth**
   - record macro shims, boxing, trait splits, and adapter costs explicitly
   - separate semantic equivalence from “works but changes the contract”
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one identical implementation strategy

## Success metrics
- Library authors can review advanced support claims without reconstructing them from issue trackers and snapshot files.
- Regressions, improvements, and workaround removals become visible as semantic diffs rather than surprise CI churn.
- Rust compiler transitions land into an ecosystem that already has a place to record what changed.
- Atlas-style guidance can recommend advanced crates with actual acceptance evidence attached.
- Docs, migration notes, and release engineering gain a stable attachment format for “what patterns are supported here and now”.

## Archive fit
This proposal fills a real gap in the archive:
- **Compile Guidance Kit** says how to package diagnostics and lint/help surfaces;
- **Trait Surface Kit** says what a trait family means semantically;
- **Lending Surface Kit** says what borrow-friendly sequence surfaces mean;
- **Spec Conformance Kit** says how to package spec-linked executable vectors.

But none of those is the portable contract for **which advanced patterns are accepted, rejected, workaround-dependent, or lane-specific right now**.
Acceptance Surface Kit is the missing substrate for that part of Rust.

## Archive fit refresh
This proposal should now be read not only as an advanced-type-system kit, but as the compiler-/pattern-facing half of a shared **compatibility-claims** frontier together with Support Envelope Kit. The strongest next execution move is a pilot program that proves stable/nightly/experimental acceptance claims, workaround truth, and release-to-release acceptance diffs can travel as explicit artifacts.

See also: `design/compatibility-claims-pilot-program.md`.
