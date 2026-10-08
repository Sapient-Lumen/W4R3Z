---
id: P-0427
title: Rust Specification Witness Kit — clause-linked executable examples, drift receipts, and qualification-friendly witness bundles
status: idea
domains: [language, specification, testing, conformance, safety-critical, tooling]
last_reviewed: 2026-03-07
evidence:
  - https://blog.rust-lang.org/2025/03/26/adopting-the-fls/
  - https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
  - https://doc.rust-lang.org/stable/reference/
  - https://docs.rs/ui_test
  - https://crates.io/crates/compiletest_rs
---

# Problem

Rust now has two important specification-adjacent realities at the same time:

- the Rust Project has adopted the FLS and explicitly wants to keep it up to date as part of its specification work,
- and Rust already has credible compiler-diagnostic and compile-fail testing substrate such as `ui_test` and `compiletest_rs`.

That means the missing crate is no longer “some kind of test harness” and no longer “some kind of spec text”.

The harder, still-missing problem is a boring default for:

- linking tiny executable examples to specific spec clauses or reference sections,
- recording whether a witness is expected to pass, fail, warn, or differ by edition/profile,
- packaging the exact compiler output and environment assumptions that justify the claim,
- and surfacing **drift receipts** when the compiler, the Reference, and the FLS stop agreeing.

The missing Rust contribution is a **specification witness kit** that turns prose claims into clause-linked, replayable, qualification-friendly artifacts.

# What it provides

- `witness.toml` — maps a witness to clause IDs, reference anchors, editions, feature flags, and expected behavior.
- `spec-map.toml` — records the document revisions and anchor conventions being used (`reference`, `fls`, local policy notes).
- `witness.receipt.json` — records toolchain, edition, flags, diagnostics, stdout/stderr, and verdict.
- `drift.report.json` — explains whether a mismatch is document drift, compiler drift, harness drift, or unresolved ambiguity.
- `witness.corpus/` — tiny clause-linked examples that can be replayed in CI.
- `cargo spec-witness` — emits `*.rustwitness.zip` bundles with code, receipts, document links, and minimized repros.

# What the crate should provide other people

1. **Clause-linked executable evidence** instead of vague “the spec says so” arguments.
2. **A standard handoff artifact** for language-team, toolchain, and safety-critical discussions.
3. **Edition- and profile-aware drift detection** across spec text and compiler behavior.
4. **A small witness corpus format** that alternative compilers, linters, teachers, and auditors can all reuse.
5. **Qualification-friendly receipts** that make it easier to explain what exactly was tested and why it mattered.

# Persona / who it’s for

- language and spec contributors
- compiler and diagnostics contributors
- safety-critical toolchain vendors and assessors
- alternative compiler authors
- educators writing “this subtle Rust rule really does behave like this” examples

# Users & user stories

- **Spec maintainer**: “Show me which witness cases anchor this clause, and whether they still agree with stable Rust.”
- **Compiler contributor**: “I changed diagnostics or behavior; tell me which spec-linked witnesses moved, and whether the move looks intentional.”
- **Safety engineer**: “Give me one bundle with the code, clause links, and exact outcome so I can review or archive it.”
- **Educator/tool author**: “Reuse the same tiny examples for docs, lint examples, and regression tests instead of keeping three divergent corpora.”

# Prior art (and why it’s insufficient)

- The Rust Reference and the FLS are real documentation surfaces.
- `ui_test` and `compiletest_rs` already support compile-fail and diagnostic-style testing.
- The compiler repo has deep in-tree testing traditions.

What Rust still lacks is a **neutral artifact layer** that makes spec clauses, editions, expected behavior, and drift verdicts portable outside one repository or one team’s local conventions.

# Design goals

1. **Clause-first** — every witness should be linkable to a specific language claim.
2. **Tiny examples** — prefer minimized witnesses over giant test suites.
3. **Drift-explicit** — disagreement must be recorded, not hidden.
4. **Qualification-friendly** — receipts should be reviewable and archivable.
5. **Harness-agnostic** — reuse existing runners where possible instead of replacing them.

# MVP surface

- Minimal types: `WitnessCase`, `ClauseRef`, `SpecMap`, `WitnessReceipt`, `DriftReport`, `WitnessBundle`
- Minimal functions:
  - `load_witness()`
  - `run_witness()`
  - `compare_expected()`
  - `classify_drift()`
  - `write_bundle()`
- Feature flags:
  - `ui-test`
  - `compiletest`
  - `miri`
  - `json-schema`
  - `redaction`

# Compatibility story

- Reuses existing Rust compiler-style test runners where helpful.
- Treats the Reference and FLS as citation targets, not as machine-interpretable truth by default.
- Can wrap compiler UI-style tests, run-pass tests, or small interpreter checks.
- Avoids requiring compiler changes for the MVP.

# Conformance & fixtures

- Edition-sensitive witnesses (`2018`/`2021`/`2024`) with explicit expected deltas.
- Clause-linked diagnostic examples for parser, type, borrow, and trait-system behavior.
- Fixtures that show “Reference and compiler agree”, “FLS and compiler agree”, and “documents disagree or lag”.
- Safe-to-share redacted witness bundles for bug reports and review.

# Path to boring stability

- Stabilize `witness.toml`, clause reference conventions, and `witness.receipt.json` before chasing many adapters.
- Keep the initial corpus intentionally tiny and representative.
- Treat drift classification as conservative and auditable.
- Prefer adapter layers around `ui_test` / `compiletest_rs` over a bespoke runner rewrite.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A crate and CLI that run a small set of clause-linked Rust examples, emit receipts, and produce a drift report when expected behavior or diagnostics change.

# De-risk plan

1. Start with a tiny corpus mapped to a handful of stable Reference/FLS clauses.
2. Reuse `ui_test` for diagnostics before inventing new execution machinery.
3. Keep drift verdicts coarse at first (`compiler-changed`, `doc-lag`, `ambiguous`).
4. Test the artifact format on educational examples as well as compiler-facing examples.

# Non-goals

- Not a replacement for the Rust Reference or the FLS.
- Not a full executable semantics of Rust.
- Not an attempt to absorb all compiler test infrastructure.
- Not a qualification claim by itself.

# Architecture & API sketch

```rust
pub struct WitnessCase {
    pub id: String,
    pub clauses: Vec<ClauseRef>,
    pub edition: String,
    pub expected: ExpectedBehavior,
}

pub fn load_witness(path: &std::path::Path) -> Result<WitnessCase>;
pub fn run_witness(case: &WitnessCase, cx: &RunContext) -> Result<WitnessReceipt>;
pub fn classify_drift(case: &WitnessCase, receipt: &WitnessReceipt) -> DriftReport;
pub fn write_bundle(bundle: &WitnessBundle, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `witness.toml`, `spec-map.toml`, `src/main.rs`, `expected/`, `receipt.json`, `drift.report.json`, `notes.md`.

# Security / safety model

- Preserve exact toolchain and flag provenance so review does not rely on memory.
- Support redaction of local paths and host metadata for shareable bundles.
- Avoid silently inferring clause links; explicit links are safer than clever guesses.
- Treat witness bundles as evidence artifacts, not proof of complete semantic coverage.

# Maintenance & governance plan

- Track Reference and FLS anchor drift explicitly in a small compatibility table.
- Keep public witness corpora tiny and curated.
- Require every new witness to cite at least one concrete clause or issue.
- Maintain adapters as thin wrappers over existing harnesses.

# Milestones

## 0.1
- `witness.toml`
- CLI to run a witness and emit a receipt
- `ui_test` adapter for diagnostic cases

## 0.2
- clause-link validation
- drift classification
- redacted `*.rustwitness.zip`

## 1.0
- stable witness bundle schema
- small public corpus
- CI/reporting helpers for spec and compiler teams

# Open questions

- What is the smallest clause-link format that survives document reorganization?
- How much diagnostic detail belongs in receipts versus derived summaries?
- Which kinds of runtime-dependent behavior should be out of scope for witness bundles?

# Sources

- Adopting the FLS: https://blog.rust-lang.org/2025/03/26/adopting-the-fls/
- FLS up-to-date capabilities goal: https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- Rust Reference: https://doc.rust-lang.org/stable/reference/
- `ui_test`: https://docs.rs/ui_test
- `compiletest_rs`: https://crates.io/crates/compiletest_rs
