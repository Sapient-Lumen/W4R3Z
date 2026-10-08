---
id: P-0446
title: Polonius Borrowck Transition Witness Kit — borrow-check outcome ledgers, NLL-vs-Polonius receipts, and minimized witness bundles for lifetime-analysis drift
status: idea
domains: [compiler, language, borrowck, testing, diagnostics, ci, devtools]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://docs.rs/ui_test
  - https://crates.io/crates/trybuild
  - https://crates.io/crates/compiletest_rs
---

# Problem

Polonius is no longer just a research codename. The Rust project has an “alpha” analysis that accepts important cases deferred from NLL, passes in-tree tests and crater runs, and is being prepared for stabilization work.

That is excellent for Rust — but it creates a very practical seam for library authors and compiler-adjacent teams:

- a crate may compile under today’s borrow checker but fail under Polonius, or vice versa,
- some changes will be welcome precision improvements while others will feel like regressions,
- diagnostic text will move around even when the semantic outcome is roughly the same,
- and today’s compile-fail harnesses can prove that behavior changed, but they do not produce a small **borrow-check witness artifact** for *what kind* of shift occurred.

The missing crate is not a new borrow checker.

The missing crate is a **transition witness layer** that helps ordinary maintainers compare old and new borrow-check behavior conservatively.

# What it provides

- `borrowck-profile.toml` — pins toolchains, channels, comparison mode, target, and case-selection policy.
- `borrowck-cases/` — fixture corpus for accepted / rejected / diagnostic-only / performance-sensitive cases.
- `borrowck.results.json` — normalized outcomes for each case under each configured toolchain/mode.
- `borrowck.diff.json` — categories such as `accepted_to_rejected`, `rejected_to_accepted`, `diagnostic_only`, `performance_only`, and `needs_manual_review`.
- `borrowck.receipt.json` — exact rustc versions, flags, environment, and caveats.
- `cargo borrowck-witness run` — executes one corpus under NLL-style and Polonius-style configurations.
- `cargo borrowck-witness diff` — compares runs and emits a conservative drift report.
- `cargo borrowck-witness reduce` — helps minimize one changed case into a small witness bundle.
- `*.borrowckbundle.zip` — shareable artifact for CI, issue filing, or team review.

# What the crate should provide other people

1. **A boring way to notice borrow-check drift early** before a language/compiler transition lands on stable.
2. **A shared vocabulary** for lifetime-analysis changes instead of screenshots and ad hoc compiler logs.
3. **A minimized handoff artifact** that compiler contributors and crate maintainers can both use.
4. **A stable-on-top workflow** above existing compile-fail harnesses.
5. **A review layer** that distinguishes “newly accepted useful pattern” from “real regression risk.”

# Persona / who it’s for

- maintainers of borrow-heavy libraries
- compiler-adjacent crate authors
- CI / release engineers comparing nightly behavior
- Rust team contributors collecting reduced witness cases

# Users & user stories

- **Library maintainer**: “Compare our lifetime-heavy test corpus under current nightly behavior and the Polonius-enabled mode.”
- **Compiler contributor**: “Attach a minimized witness bundle to a fixed-by-polonius or NLL-deferred issue.”
- **Release engineer**: “Separate semantic changes from diagnostic churn before we flag a nightly bump.”
- **Educator / book maintainer**: “Record that this example moved from rejected to accepted, and why we think that is legitimate.”

# Prior art (and why it’s insufficient)

- The Polonius project-goal page makes clear that the analysis is becoming practical enough to expose to users.
- `ui_test`, `trybuild`, and `compiletest_rs` already help capture compile-time expectations.

What remains missing is a **borrow-check drift witness** above those harnesses: a receipt format that treats toolchain/mode differences as first-class review artifacts.

# Design goals

1. **Outcome-first** — compare accepted/rejected/diagnostic-only categories before chasing internal facts.
2. **Conservative** — when cause attribution is unclear, say so.
3. **Harness-friendly** — reuse existing compile-fail corpora where possible.
4. **Issue-ready** — minimized witnesses should be easy to hand to humans and upstream.
5. **Distinct from trait-solver work** — this crate is about lifetime-analysis outcomes, not trait-obligation reasoning.

# MVP surface

- Minimal types: `BorrowckProfile`, `BorrowckCase`, `BorrowckOutcome`, `BorrowckDiff`, `BorrowckReceipt`, `BorrowckBundle`
- Minimal functions:
  - `run_case_corpus()`
  - `normalize_outcome()`
  - `diff_runs()`
  - `classify_change()`
  - `write_bundle()`
- Feature flags:
  - `ui-test`
  - `trybuild`
  - `serde`
  - `cargo`
  - `minimizer`

# Compatibility story

- Reuses existing compile-fail corpora where practical.
- Treats rustc as the source of truth; it does not attempt to reimplement borrow checking.
- Should work with stable/beta/nightly comparison sets where relevant, but the most useful early mode will be nightly-vs-nightly experiments.
- Can degrade to “diagnostic drift only” when semantic classification is unclear.

# Conformance & fixtures

- Fixtures for classic NLL-deferred patterns, lending-iterator-adjacent cases, mutation-after-borrow patterns, and false-positive reductions.
- Goldens for “accepted on both”, “rejected on both with different wording”, “rejected→accepted”, and “accepted→rejected”.
- Corpus adapters for `ui_test` and `trybuild`.
- Reduced witness examples small enough for issue trackers.

# Path to boring stability

- Stabilize a narrow outcome taxonomy first.
- Keep the receipt schema independent of unstable internal compiler debug dumps.
- Prefer explicit uncertainty to clever but fragile root-cause inference.
- Add richer minimization and categorization only after the core workflow is trusted.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that run a small lifetime-sensitive corpus across two borrow-check configurations, classify the differences conservatively, and emit a `borrowck.diff.json` plus a shareable witness bundle.

# De-risk plan

1. Start with outcome normalization only; do not depend on unstable internal fact dumps.
2. Support one existing corpus format first.
3. Keep classification buckets few and reviewable.
4. Validate usefulness on one real open-source crate with known borrow-check edge cases.

# Non-goals

- Not a borrow checker implementation.
- Not a promise to explain every lifetime-analysis root cause.
- Not a replacement for upstream compiler issue triage.
- Not a generic compile-fail framework.

# Architecture & API sketch

```rust
pub enum BorrowckOutcomeKind {
    Accepted,
    Rejected,
    DiagnosticOnly,
    Timeout,
    Ice,
    Unknown,
}

pub fn run_case_corpus(profile: &BorrowckProfile, corpus: &Path) -> Result<BorrowckRun>;
pub fn diff_runs(old: &BorrowckRun, new: &BorrowckRun) -> BorrowckDiff;
pub fn classify_change(old: &BorrowckOutcome, new: &BorrowckOutcome) -> ChangeClass;
pub fn write_bundle(bundle: &BorrowckBundle, out: &Path) -> Result<()>;
```

Bundle draft: `borrowck-profile.toml`, `cases/`, `borrowck.results.json`, `borrowck.diff.json`, `borrowck.receipt.json`, `notes.md`.

# Security / safety model

- Never infer semantic equivalence from matching diagnostics alone.
- Support path and crate-name redaction in shared bundles.
- Record exact toolchain identifiers and flags.
- Keep minimized witnesses deterministic and reviewable.

# Maintenance & governance plan

- Version the outcome taxonomy carefully.
- Maintain a small public corpus of representative borrow-check edge cases.
- Keep harness adapters optional and thin.
- Publish guidance for interpreting “diagnostic only” versus semantic drift.

# Milestones

## 0.1
- one corpus format
- run/diff workflow
- narrow taxonomy

## 0.2
- reduction helpers
- second corpus adapter
- bundle export

## 1.0
- stable receipt schema
- CI/report adapters
- curated public corpus

# Open questions

- What is the smallest useful borrow-check drift taxonomy?
- Which outcome categories map best to real downstream pain?
- How much performance/regression information belongs in the same witness bundle?

# Sources

- Polonius goal: https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `ui_test`: https://docs.rs/ui_test
- `trybuild`: https://crates.io/crates/trybuild
- `compiletest_rs`: https://crates.io/crates/compiletest_rs
