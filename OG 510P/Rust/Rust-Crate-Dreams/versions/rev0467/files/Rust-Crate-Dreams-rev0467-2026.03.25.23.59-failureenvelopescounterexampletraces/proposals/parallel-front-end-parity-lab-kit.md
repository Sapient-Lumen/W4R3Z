---
id: P-0450
title: Parallel Front-End Parity Lab Kit — single-vs-parallel receipts, deadlock repro bundles, and workload-aware performance ledgers for rustc front-end adoption
status: idea
domains: [compiler, build, performance, testing, ci, cargo, tooling, diagnostics]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/parallel-front-end.html
  - https://github.com/rust-lang/rust/issues/113349
  - https://github.com/rust-lang/rustc-perf
  - https://github.com/rust-lang/rustc-perf/issues/2068
---

# Problem

Rust’s parallel front end is no longer just a compiler-lab curiosity. The Rust project is explicitly working toward stabilization, reports 20–30%+ compile-time wins in some cases, and is now treating surrounding tool support in Cargo, bootstrap, and rustc-perf as part of the real adoption story.

That is a major opportunity — but it also opens a practical gap for ordinary maintainers and tool authors:

- they need to know whether parallel front end is **behaviorally consistent** with single-threaded compilation for *their* workloads,
- they need a compact way to capture **hangs, deadlocks, or diagnostic drift**,
- they need something more workload-shaped than a raw benchmark dashboard,
- and they need a portable artifact they can hand to upstream when “works fine with `-Z threads=1`, flakes with `-Z threads=8`”.

The missing crate is not a new compiler profiler.

The missing crate is a **parity lab** that turns parallel-front-end adoption into a reviewable, reproducible workflow.

# What it provides

- `parity-profile.toml` — pins toolchains, thread counts, workload commands, timeout policy, and comparison rules.
- `parity-cases/` — reusable workload definitions for `check`, `build`, `test`, `rustdoc`, and macro-heavy stress cases.
- `parity.results.json` — normalized outcome records for each run: success, timeout, deadlock suspicion, ICE, diagnostic drift, and timing metrics.
- `parity.diff.json` — categories such as `same_output_faster`, `same_output_slower`, `deadlock_only`, `ice_only`, `diagnostic_only`, and `cargo_integration_gap`.
- `parity.receipt.json` — rustc/cargo versions, thread settings, machine facts, environment flags, and caveats.
- `cargo front-parity run` — execute one or more workload suites under pinned thread settings.
- `cargo front-parity diff` — compare single-thread and parallel-front-end runs.
- `cargo front-parity bundle` — emit a small repro bundle for CI review or upstream bug reports.
- `*.paritybundle.zip` — shareable artifact containing configs, logs, reduced repro commands, and diff summaries.

# What the crate should provide other people

1. **A boring adoption gate** for “can we try parallel front end on this workspace yet?”
2. **A shared vocabulary** for parity failures instead of screenshots and hand-written shell notes.
3. **A compact upstream handoff artifact** when deadlocks, hangs, or drifts appear.
4. **A stable-on-top workflow** above raw compiler flags, ad hoc benchmarking, and bespoke CI matrices.
5. **A tool-facing receipt format** that Cargo-adjacent and IDE-adjacent tools can consume.

# Persona / who it’s for

- maintainers of large Rust workspaces
- compiler-adjacent crate authors
- CI / build engineers testing nightly features
- Cargo and IDE tooling authors
- compiler contributors collecting reproductions

# Users & user stories

- **Workspace maintainer**: “Compare `cargo check` and `cargo test` under one-thread and parallel-front-end settings before enabling it in CI experiments.”
- **Compiler contributor**: “Attach a reduced parity bundle to the tracking issue instead of a giant terminal paste.”
- **Tooling author**: “See whether our rustdoc or Cargo integration behaves differently once parallel front end is on.”
- **Release engineer**: “Separate real semantic drift from mere timing noise and flaky hangs.”

# Prior art (and why it’s insufficient)

- The project goal, tracking issue, and rustc-perf work show that the Rust project is already doing serious compiler-facing performance and robustness work.
- rustc-perf is excellent for compiler development, but it is not a maintainer-facing crate workflow for ordinary workspaces.
- The parallel-front-end test suite helps rustc itself, but it does not standardize a downstream artifact story.

What remains missing is a **parity receipt layer** above flags, perf dashboards, and ad hoc repro notes.

# Design goals

1. **Consistency-first** — correctness and parity classification come before speed claims.
2. **Workload-oriented** — compare realistic Cargo/rustdoc workloads, not only microbenchmarks.
3. **Hang-aware** — timeouts and suspected deadlocks must be first-class artifact states.
4. **Tool-friendly** — keep receipts readable by CI, Cargo wrappers, and IDE tools.
5. **Conservative** — when a cause is unclear, say so instead of inventing compiler certainty.

# MVP surface

- Minimal types: `ParityProfile`, `ParityCase`, `ParityRun`, `ParityDiff`, `ParityReceipt`, `ParityBundle`
- Minimal functions:
  - `run_workloads()`
  - `normalize_outcomes()`
  - `diff_runs()`
  - `reduce_repro()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `rustdoc`
  - `perf-stats`

# Compatibility story

- Treats rustc and Cargo as the source of truth; it does not reimplement compiler scheduling logic.
- Should work even before stabilization by operating in explicit experimental mode.
- Can degrade to “timing and exit-status only” when deeper diagnostics are unavailable.
- Must keep machine-specific effects visible instead of pretending all parity failures are toolchain-only.

# Conformance & fixtures

- Macro-heavy crates, rustdoc-heavy crates, test-heavy crates, and medium-size workspaces.
- Goldens for “same output, faster”, “same output, slower”, “timeout only in parallel mode”, and “diagnostic-only drift”.
- Fixture support for pinned toolchains and reproducible command lines.
- Example bundles suitable for issue trackers.

# Path to boring stability

- Stabilize the receipt and diff taxonomy before adding lots of heuristics.
- Start with a narrow set of workload kinds.
- Prefer compact reduced repro commands over giant full-workspace captures.
- Keep rustc-perf integration optional and thin.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that run one workspace under `threads=1` and one parallel-front-end setting, classify success/hang/diagnostic drift/timing differences, and emit a shareable parity bundle.

# De-risk plan

1. Start with `cargo check` and `cargo build` only.
2. Keep the first diff taxonomy small and obvious.
3. Record timeouts/hangs as first-class outcomes rather than trying to explain them too early.
4. Test usefulness on one macro-heavy and one docs-heavy workspace before widening scope.

# Non-goals

- Not a replacement for rustc-perf.
- Not a general-purpose benchmark harness.
- Not a promise to pinpoint the exact compiler root cause of every drift.
- Not a stable API guarantee for internal compiler telemetry.

# Architecture & API sketch

```rust
pub enum ParityOutcomeKind {
    Success,
    Timeout,
    DeadlockSuspected,
    Ice,
    DiagnosticDrift,
    Unknown,
}

pub fn run_workloads(profile: &ParityProfile, root: &Path) -> Result<ParityRunSet>;
pub fn diff_runs(serial: &ParityRunSet, parallel: &ParityRunSet) -> ParityDiff;
pub fn reduce_repro(diff: &ParityDiff) -> Option<ReducedRepro>;
pub fn write_bundle(bundle: &ParityBundle, out: &Path) -> Result<()>;
```

Bundle draft: `parity-profile.toml`, `commands.json`, `parity.results.json`, `parity.diff.json`, `parity.receipt.json`, `logs/`, `notes.md`.

# Security / safety model

- No hidden telemetry upload in the MVP.
- Support path redaction and workspace-name redaction in exported bundles.
- Keep machine metadata explicit but minimal.
- Preserve exact command lines and toolchain identifiers for replay.

# Maintenance & governance plan

- Version the diff taxonomy carefully.
- Maintain a small public fixture corpus of representative parity failures.
- Keep Cargo/rustdoc adapters separate from the core receipt model.
- Publish guidance on interpreting timing deltas versus correctness deltas.

# Milestones

## 0.1
- serial vs parallel run support
- receipt schema
- basic diff categories

## 0.2
- reduced repro bundles
- rustdoc workload support
- timeout/deadlock heuristics

## 1.0
- stable receipt format
- CI adapters
- optional rustc-perf export hooks

# Open questions

- Which workload shapes reveal the most useful parity failures for ordinary users?
- How should machine-specific timing noise be represented without hiding it?
- What is the narrowest useful set of diff categories for compiler adoption review?

# Sources

- Promoting Parallel Front End: https://rust-lang.github.io/rust-project-goals/2025h2/parallel-front-end.html
- Parallel front-end tracking issue: https://github.com/rust-lang/rust/issues/113349
- `rustc-perf`: https://github.com/rust-lang/rustc-perf
- rustc-perf issue for parallel front-end testing: https://github.com/rust-lang/rustc-perf/issues/2068
