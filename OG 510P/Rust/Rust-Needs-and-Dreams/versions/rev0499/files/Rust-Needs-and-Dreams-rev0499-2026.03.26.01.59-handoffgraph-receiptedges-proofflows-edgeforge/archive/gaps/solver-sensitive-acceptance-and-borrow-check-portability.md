# Gap: solver-sensitive acceptance and borrow-check portability are still too implicit

## What is missing
Rust is actively changing the machinery that decides whether advanced code patterns compile at all, but the ecosystem still lacks a **portable way to publish acceptance truth** for those patterns.

Today there is no standard way to say:
- which solver- or borrow-check-sensitive patterns a crate intentionally supports,
- which examples are expected to compile, fail, or remain unsupported,
- which results were checked on stable, beta, nightly, `-Znext-solver=globally`, or Polonius,
- which failures are considered acceptable current limits versus regressions,
- which workaround formulations preserve semantics and which only approximate them,
- and which acceptance claims are backed by executable evidence instead of issue links and lore.

That gap matters more now because Rust’s roadmap is not treating these as hypothetical corners. The 2026 flagships explicitly aim to **stabilize the next-generation trait solver** and frame lending iterators / evolvable trait hierarchies as part of the “unblocking dormant traits” agenda. The 2025H2 next-solver goal says the work should replace the existing trait-solver implementation entirely and extend into lints and rustdoc. The 2025H2 Polonius goal says the nightly implementation should accept lending iterators and be good enough for crater/CI/stabilization work. And the evolving-traits goal is directly about trait-family refactors like `Deref: Receiver`, `Iterator: LendingIterator`, and local/send split families.

So the missing contribution is not one more advanced-traits crate, not one more blog post full of caveats, and not one more local `tests/ui` directory.
It is a **reviewable acceptance-surface layer** for publishing what advanced Rust patterns are actually supported, under which compiler lanes, with which workarounds, and with what evidence.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
- https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html

## The current seam is awkward
Rust already has good testing primitives, but they do not add up to a shared ecosystem contract:
- the compiler itself uses `compiletest` and large UI test suites, with directives, revisions, blessed snapshots, and explicit pass/fail control;
- `trybuild` gives library authors a lightweight harness for compile-fail and pass tests checked against `.stderr` snapshots;
- `ui_test` offers a more configurable runner that can drive `rustc` or Cargo and compare compiler output checked into git;
- the next-solver goal explicitly asks users to test `-Znext-solver=globally` and says more lints and rustdoc should move to the new solver;
- the Polonius goal already includes a debugging / dump tool for the location-sensitive analysis.

That means the ecosystem is not missing *ways to run tests*.
It is missing the **artifact family that records which patterns are being claimed, which compiler lane was exercised, which outcomes were expected, which workarounds were used, and how those outcomes changed over time**.

Sources:
- https://rustc-dev-guide.rust-lang.org/tests/compiletest.html
- https://rustc-dev-guide.rust-lang.org/tests/ui.html
- https://docs.rs/trybuild
- https://docs.rs/ui_test
- https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html

## Why this matters
This gap matters because some of Rust’s hardest ecosystem work now depends on **accepted/rejected pattern truth**, not just API docs:
1. **trait-heavy libraries** — async traits, RTN-heavy APIs, split local/send families, associated-type bounds, and trait-family refactors all depend on what the compiler currently accepts;
2. **borrow-sensitive APIs** — lending iterators, borrowing streams, reborrow-heavy wrappers, and future Polonius-enabled patterns need explicit “works here / fails here” evidence;
3. **compiler-transition resilience** — next-solver and Polonius are supposed to be largely backwards-compatible, but advanced crates still need a reviewable way to spot improvements, regressions, and changed workarounds;
4. **tooling and docs** — lints, rustdoc, guides, examples, and migration notes increasingly need to state not only the desired pattern but the currently accepted one;
5. **release and CI governance** — crates that live near the edge of Rust’s type and borrow systems need machine-readable evidence for “supported on stable”, “nightly experiment only”, or “future lane guarded by workaround”.

A worthy contribution here is therefore not another solver experiment or another diagnostics snapshot runner.
It is a way to treat **acceptance surfaces as reviewable ecosystem infrastructure**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
- https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://docs.rs/trybuild
- https://docs.rs/ui_test

## What “good” looks like
A worthy contribution here is **not** a universal compiler-test runner and not a fake guarantee that every crate should care about every experimental lane.

It is a shared acceptance-surface boundary:
- one `acceptance-subject/v0` describing the crate / module / pattern family under review,
- one `pattern-catalog/v0` describing named accepted, rejected, and intentionally-unsupported code-pattern families,
- one `compiler-lane-profile/v0` describing stable/beta/nightly and optional experimental lanes like next-solver or Polonius,
- one `acceptance-expectation-set/v0` describing expected pass/fail/xfail posture and reason classes,
- one `workaround-profile/v0` describing alternate formulations, macro shims, adapter traits, or local/send split lanes that preserve or lose semantics,
- one `acceptance-check-report/v0` recording what actually happened,
- one `acceptance-diff-report/v0` describing regressions, newly accepted patterns, changed reasons, or dropped workarounds,
- and one `acceptance-pack/v0` bundle for docs, CI, release notes, and archaeology.

That would let Rust teams review advanced-type / borrow-support claims using explicit artifacts instead of reconstructing them from issue links, compiler snapshots, hand-written README caveats, and whatever happened to be in `tests/ui` this month.

## Non-goals
This gap should not be used to:
- replace `compiletest`, `trybuild`, or `ui_test`,
- bless one experimental compiler lane as the truth before stabilization,
- flatten diagnostic wording and semantic acceptance into one artifact,
- or pretend every library should start carrying a full compiler-regression matrix.

The job is smaller and sharper:
**make solver- and borrow-check-sensitive acceptance claims legible, honest, and diffable while Rust is evolving the machinery behind them.**
