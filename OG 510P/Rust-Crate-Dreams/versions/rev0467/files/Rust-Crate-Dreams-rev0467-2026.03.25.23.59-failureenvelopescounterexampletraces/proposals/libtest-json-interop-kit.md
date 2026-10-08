---
id: P-0463
title: Libtest JSON Interop Kit — schema locks, suite-aware run receipts, and harness-bridge bundles for Cargo, nextest, libtest-mimic, and future programmatic test runners
status: idea
domains: [testing, cargo, libtest, ci, diagnostics, tooling, harnesses]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
  - https://rust-lang.github.io/rfcs/3558-libtest-json.html
  - https://crates.io/crates/cargo-nextest
  - https://nexte.st/docs/machine-readable/libtest-json/
  - https://crates.io/crates/libtest-mimic
---

# Problem

Rust is actively working on machine-readable **libtest JSON output** because today’s testing story leaves too much information trapped in human-oriented streams. The project goal and RFC both make the same point: Cargo wants richer programmatic output, custom test runners want a lower-friction protocol, and runners like `cargo-nextest` already need to interoperate with unstable or partial formats.

That still leaves a missing ecosystem layer:

- the upstream format is evolving, so ordinary teams lack a boring **schema lock** they can review,
- Cargo, `libtest`, `cargo-nextest`, and custom harnesses still do not share one compact artifact for suite names, binary boundaries, and failure semantics,
- downstream tools often jump straight to JUnit, losing Rust-specific structure or producing awkward mappings,
- and test infrastructure owners still lack a conservative bundle for comparing “what the runner saw” versus “what Cargo or CI consumed.”

The missing crate is not a new test runner.

The missing crate is an **interop kit** that treats libtest-style JSON as a first-class exchange artifact across Cargo, nextest, custom harnesses, IDEs, and CI systems.

# What it provides

- `libtest-schema.lock` — pins the expected event vocabulary, required fields, optional extensions, and compatibility policy.
- `test-list.receipt.json` — normalized discovered tests, suites, binaries, locations, and ignored/bench metadata.
- `test-run.receipt.json` — canonical event log with suite-aware IDs, binary attribution, elapsed timing, and exit-status normalization.
- `test-interop.diff.json` — records where two runners or schema versions differ.
- `failure-bundle/` — per-failure attachments, stdout/stderr references, rendered diagnostics, and optional seed/tempdir metadata.
- `runner-bridge.toml` — mapping policy for Cargo, nextest, libtest-mimic, and local harness adapters.
- `cargo test-interop capture` — capture one run as a normalized receipt.
- `cargo test-interop compare` — compare two machines/runners/schema versions.
- `cargo test-interop export` — write JUnit/TAP/subunit projections while preserving a Rust-native receipt.
- `*.testrunbundle.zip` — shareable artifact for CI, IDE integration, or upstream feedback.

# What the crate should provide other people

1. **A boring schema lock** around a still-evolving programmatic test protocol.
2. **A suite-aware receipt** that survives multiple binaries and different runners.
3. **A bridge artifact** between Rust-native test output and generic CI formats.
4. **A comparison bundle** for runner drift, flaky behavior triage, and output regressions.
5. **A path for custom harnesses** to emit something more stable-on-top than raw unstable JSON.

# Persona / who it’s for

- CI and developer-experience engineers
- maintainers of large workspaces using `cargo test` and `cargo nextest`
- custom test-harness authors
- IDE/tool authors that need structured locations and failure metadata

# Users & user stories

- **CI owner**: “Keep a Rust-native receipt, but also export JUnit for the legacy dashboard.”
- **Runner author**: “Show me where our output diverges from expected libtest-style events.”
- **IDE/tooling author**: “Give me stable-enough locations, suite names, and failure attachments without scraping terminal output.”
- **Workspace maintainer**: “Compare `cargo test` and `cargo nextest` results for the same build and see what semantics differ.”

# Prior art (and why it’s insufficient)

- The project goal and RFC explain why machine-readable libtest output matters and why Cargo wants to build richer UX on top of it.
- `cargo-nextest` and its machine-readable formats prove downstream demand is real.
- `libtest-mimic` and other custom harnesses show there is already a nontrivial test-runner ecosystem.

What remains missing is a **maintainer-facing interop artifact layer**: a schema lock, suite-aware receipt, and bridge bundle that ordinary tools can exchange and review.

# Design goals

1. **Schema-first** — make compatibility policy explicit.
2. **Suite-aware** — preserve binary and suite boundaries that generic CI formats often blur.
3. **Runner-neutral on top** — useful with Cargo, nextest, and custom harnesses.
4. **Attachment-friendly** — keep room for diagnostics, seeds, tempdirs, and future metrics.
5. **Stable-on-top** — useful even while upstream formats evolve.

# MVP surface

- Minimal types: `LibtestSchemaLock`, `TestListReceipt`, `TestRunReceipt`, `InteropDiff`, `RunnerBridge`, `TestRunBundle`
- Minimal functions:
  - `capture_run()`
  - `normalize_events()`
  - `compare_receipts()`
  - `export_projection()`
  - `write_bundle()`
- Feature flags:
  - `serde`
  - `cargo`
  - `nextest`
  - `junit`
  - `tap`

# Compatibility story

- Must be useful before stabilization by wrapping today’s experimental output conservatively.
- Should remain useful after stabilization because teams will still need schema locks, comparisons, and export bridges.
- Must tolerate partial-fidelity sources and mark extensions as such.
- Should preserve unknown fields instead of discarding them.

# Conformance & fixtures

- One standard `libtest` binary with passes, failures, ignored tests, and benches.
- One `cargo-nextest` run projected into the same receipt vocabulary.
- One `libtest-mimic` fixture with custom discovery.
- Goldens for multi-binary suite mapping, JUnit projection, unexpected-exit handling, and output-drift classification.
- Location-rich fixtures for IDE consumption.

# Path to boring stability

- Stabilize a narrow schema-lock format first.
- Start with capture + normalize + compare.
- Treat generic export formats as projections, not the source of truth.
- Add richer attachments only after the basic receipt is trusted.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 5/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that capture one `cargo test` or `cargo nextest` run into a normalized suite-aware receipt, compare it to another run, and export a compact bridge bundle with a pinned schema lock.

# De-risk plan

1. Start with capture and normalization, not rewriting runners.
2. Support Cargo/libtest and nextest first.
3. Preserve unknown events and extension fields.
4. Validate usefulness with one CI consumer and one IDE-style consumer.

# Non-goals

- Not a replacement for `cargo test`, `cargo-nextest`, or `libtest-mimic`.
- Not a promise that upstream format churn disappears.
- Not a generic test analytics SaaS.
- Not a benchmark framework.

# Architecture & API sketch

```rust
pub struct LibtestSchemaLock {
    pub version: String,
    pub extensions: Vec<String>,
}

pub fn capture_run(cfg: &CaptureConfig) -> Result<TestRunReceipt>;
pub fn normalize_events(raw: &[RawEvent]) -> Result<TestRunReceipt>;
pub fn compare_receipts(a: &TestRunReceipt, b: &TestRunReceipt) -> InteropDiff;
pub fn write_bundle(bundle: &TestRunBundle, out: &Path) -> Result<()>;
```

Bundle draft: `libtest-schema.lock`, `test-list.receipt.json`, `test-run.receipt.json`, `test-interop.diff.json`, `runner-bridge.toml`, `failure-bundle/`, `notes.md`.

# Security / safety model

- Never drop unknown fields silently.
- Preserve exact runner/toolchain identity in receipts.
- Support redaction of file paths and test names for shared bundles.
- Keep projections lossy-but-labeled when exporting to JUnit or TAP.

# Maintenance & governance plan

- Track the libtest JSON experiment and stabilization process closely.
- Keep the schema-lock format small and versioned.
- Maintain fixture corpora spanning Cargo, nextest, and at least one custom harness.
- Publish compatibility guidance for extension fields and suite mapping.

# Milestones

## 0.1
- schema lock
- capture + normalize
- bundle export

## 0.2
- runner comparison
- JUnit/TAP projections
- custom-harness adapter example

## 1.0
- stable receipt schema
- CI/IDE adapters
- public fixture corpus

# Open questions

- What is the smallest suite-aware receipt that still survives multiple binaries and future custom harnesses?
- Which fields should remain extensions rather than part of the core lock?
- How should partial-fidelity nextest projections be labeled without making the artifact unusable?

# Sources

- Libtest JSON goal: https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- RFC 3558 libtest JSON: https://rust-lang.github.io/rfcs/3558-libtest-json.html
- `cargo-nextest`: https://crates.io/crates/cargo-nextest
- nextest libtest JSON docs: https://nexte.st/docs/machine-readable/libtest-json/
- `libtest-mimic`: https://crates.io/crates/libtest-mimic
