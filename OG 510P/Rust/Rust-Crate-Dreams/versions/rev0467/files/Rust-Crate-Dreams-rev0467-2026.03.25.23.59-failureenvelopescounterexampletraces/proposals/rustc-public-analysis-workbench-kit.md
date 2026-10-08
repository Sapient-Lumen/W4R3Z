---
id: P-0429
title: rustc_public Analysis Workbench Kit — compatibility locks, analyzer fixtures, and cross-tool evidence bundles
status: idea
domains: [compiler, tooling, static-analysis, verification, devtools]
last_reviewed: 2026-03-16
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
  - https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
  - https://github.com/rust-lang/compiler-team/issues/949
  - https://github.com/rust-lang/project-stable-mir
  - https://doc.rust-lang.org/nightly/nightly-rustc/rustc_public/index.html
---

# Problem

Rust now has enough **official** public-compiler-interface momentum that the missing crate is no longer “please expose something from rustc.”

The official substrate is real:

- the 2025H1 StableMIR goal was accepted specifically to publish a SemVer-aware compiler interface on crates.io,
- the 2025 GSoC result says the hard refactoring and dual-maintenance infrastructure for `rustc_public` / `rustc_public_bridge` were completed,
- the compiler-team MCP for publishing `rustc_public` now spells out a dual-repository, multi-compiler-version model,
- and the current nightly `rustc_public` docs already expose an explicit split between SemVer-oriented public APIs and modules like `rustc_internal` / `unstable` that are **not** meant to count toward SemVer.

That is excellent news for the ecosystem.
It also sharpens the next missing layer.

Tool authors still do not have a boring shared answer to questions like:

- which `rustc_public` version and compiler range a given analyzer actually supports,
- whether a tool stayed inside the intended SemVer surface or quietly relied on `unstable` / `rustc_internal` details,
- how to share a minimized failing case when one analyzer or one compiler version regresses,
- how to compare two tools on the same fixture without inventing incompatible snapshot formats,
- and what artifact should a maintainer or researcher inspect instead of bespoke test harnesses, screenshots, and “works on my nightly” prose.

The missing crate is **not** `rustc_public` itself.
The missing crate is a **rustc_public analysis workbench**: a fixture-first crate and cargo-adjacent tool that turns compiler-interface adoption into **compatibility locks, analyzer fixtures, capability matrices, and diffable evidence bundles**.

# What it provides

- `publicir.lock` — pins compiler channel/range, `rustc_public` version range, bridge mode, edition, crate features, and redaction posture.
- `analyzer-fixture.toml` — declares one minimized fixture: crate root, selected items/functions, expected extraction mode, and language-feature tags.
- `ir.snapshot.json` — normalized extracted public-IR fragments for comparison and goldens.
- `tool-compat.matrix.json` — records which compiler versions / `rustc_public` versions / bridge modes a tool claims and has actually exercised.
- `capability.matrix.json` — records analyzer support for language/IR families (`async`, generators, closures, traits, layout queries, unsafe ops, etc.).
- `analysis.receipt.json` — records findings, unsupported constructs, extraction warnings, and whether any semver-exempt surfaces were touched.
- `publicir.diff.json` — compares two receipts or snapshots and classifies `compatible`, `capability_gap`, `snapshot_drift`, `unstable_surface_touched`, `bridge_required`, and `manual_review_required`.
- `cargo publicir capture` — build one minimized fixture bundle for one tool.
- `cargo publicir diff <old> <new>` — compare tool / compiler / `rustc_public` results.
- `cargo publicir compat` — emit or verify a tool compatibility matrix.
- `*.publicirbundle.zip` — portable regression / review / migration artifact.

# What the crate should provide other people

1. **A compatibility lock** that makes `rustc_public`-based tools reproducible enough to review.
2. **A shared fixture format** for analyzers, verifiers, and compiler-adjacent tools.
3. **An unstable-leak report** when a tool relies on `rustc_internal` / `unstable` surfaces outside the intended SemVer contract.
4. **A cross-tool comparison artifact** that helps researchers and maintainers compare behavior on the same minimized case.
5. **A migration handoff bundle** for tools moving from `rustc_private`-style integrations to `rustc_public`.

# Persona / who it’s for

- authors of analyzers, verifiers, linters, and compiler-adjacent devtools
- maintainers migrating off unstable compiler-internal integrations
- researchers comparing multiple Rust analysis tools
- platform teams curating internal toolchains around one supported compiler window
- incident/debugging teams investigating tool regressions after a compiler update

# Users & user stories

- **Analyzer author**: “Pin exactly which compiler / `rustc_public` ranges my tool supports, and export one minimized bundle when a nightly breaks.”
- **Tool maintainer**: “Tell me if we stayed inside the SemVer-shaped public API or quietly touched unstable bridge surfaces.”
- **Researcher**: “Run two tools on one fixture and compare capability gaps without reverse-engineering their private formats.”
- **Platform team**: “Keep one compatibility matrix for the `rustc_public` tools we permit in CI.”
- **Migration owner**: “Show the delta between our old compiler-internal integration and the new public-IR path.”

# Prior art (and why it’s insufficient)

- The accepted StableMIR / `rustc_public` goal is the **compiler substrate**, not the cross-tool coordination layer.
- The project-stable-mir / Rustc Librarification project now has a real getting-started and migration story, which is great for individual tool adoption.
- The compiler-team publishing MCP is focused on repository structure, versioning, and maintenance for `rustc_public` itself.
- Individual tools like Kani, MiniRust, KMIR, and others are beginning to adopt `rustc_public`, but each tends to bring its own fixtures, compatibility assumptions, and reporting.

What remains missing is a **neutral workbench layer** above `rustc_public`:
a shared way to lock compatibility, freeze fixtures, publish capability reports, and classify semver-exempt usage.

# Design goals

1. **Compatibility-first** — compiler range and `rustc_public` range are first-class facts, not README prose.
2. **Fixture-small** — minimized failing cases should be cheap to share and rerun.
3. **Unstable-leak-aware** — touching semver-exempt surfaces must be visible, not an implementation detail.
4. **Cross-tool** — one bundle should be reusable across analyzers and reviews.
5. **Bundle-first** — the output should survive past CI logs and ad hoc screenshots.

# MVP surface

- Minimal types: `PublicIrLock`, `AnalyzerFixture`, `IrSnapshot`, `ToolCompatMatrix`, `CapabilityMatrix`, `AnalysisReceipt`, `PublicIrDiff`, `PublicIrBundle`
- Minimal functions:
  - `capture_fixture_bundle()`
  - `normalize_snapshot()`
  - `record_tool_compatibility()`
  - `classify_unstable_surface_usage()`
  - `diff_receipts()`
  - `write_bundle()`
- Feature flags:
  - `snapshot-json`
  - `serde`
  - `diff`
  - `markdown`
  - `html-report`

# Compatibility story

- Works best when tools already use `rustc_public` as their primary compiler integration surface.
- Must distinguish:
  - public SemVer-covered `rustc_public` facts,
  - semver-exempt `rustc_internal` / `unstable` usage,
  - and tool-local assumptions not observed directly.
- Should remain useful even before `rustc_public` is fully published on crates.io by treating compiler/nightly provenance as a first-class fact.
- Must not pretend to replace the compiler-team’s own release engineering for `rustc_public`.
- Should compose with tool-local reports, formal methods, and verification bundles instead of replacing them.

# Conformance & fixtures

- Tiny fixtures for traits, closures, async functions, unsafe operations, layout queries, and cross-crate calls.
- One fixture family for “same source, different compiler / `rustc_public` window”.
- One fixture family for “tool claims support, but capability matrix says partial”.
- One fixture family for “semver-exempt surface touched; quarantine this result”.
- Goldens for `compatible`, `capability_gap`, `snapshot_drift`, `unstable_surface_touched`, `bridge_required`, and `manual_review_required`.

# Path to boring stability

- Freeze the lockfile, capability matrix, and analysis receipt before adding many exporters.
- Start with one-tool capture and two-receipt diffing before ambitious orchestration.
- Keep the unstable-surface taxonomy coarse and reviewable.
- Prefer explicit partial support claims over overconfident “supported” marketing.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that pin compiler / `rustc_public` compatibility for one tool, capture one minimized fixture, emit one capability matrix plus one analysis receipt, and diff that bundle against another tool or compiler run.

# De-risk plan

1. Start with fixture capture and compatibility reporting, not multi-tool orchestration across the whole ecosystem.
2. Keep the language-feature taxonomy small and extensible.
3. Treat semver-exempt surface use as a first-class review result, not a hidden implementation detail.
4. Validate the schema on one migration-style tool and one greenfield `rustc_public` tool.

# Non-goals

- Not a replacement for `rustc_public` itself.
- Not a `rustc_private` façade or shim layer.
- Not a whole-program optimizer or verifier.
- Not a generic compiler-frontend protocol for every possible Rust IR.

# Architecture & API sketch

```rust
pub struct PublicIrLock {
    pub compiler_channel: String,
    pub compiler_range: String,
    pub rustc_public_range: String,
    pub bridge_mode: String,
    pub edition: String,
    pub features: Vec<String>,
}

pub struct ToolCompatRow {
    pub tool_name: String,
    pub compiler_range: String,
    pub rustc_public_range: String,
    pub semver_exempt_surfaces: Vec<String>,
    pub status: String,
}

pub fn capture_fixture_bundle(spec: &AnalyzerFixture, cx: &CaptureContext) -> Result<PublicIrBundle>;
pub fn record_tool_compatibility(report: &RunReport) -> ToolCompatRow;
pub fn classify_unstable_surface_usage(snapshot: &IrSnapshot) -> UnstableSurfaceReport;
pub fn diff_receipts(old: &AnalysisReceipt, new: &AnalysisReceipt) -> PublicIrDiff;
```

Bundle draft: `publicir.lock`, `analyzer-fixture.toml`, `src/`, `ir.snapshot.json`, `tool-compat.matrix.json`, `capability.matrix.json`, `analysis.receipt.json`, `publicir.diff.json`, `notes.md`.

# Security / safety model

- Support redaction and minimization for proprietary source fixtures.
- Preserve compiler provenance so tool failures remain reproducible.
- Never silently upgrade semver-exempt surface use into a clean compatibility claim.
- Distinguish “unsupported construct”, “tool bug”, “compiler drift”, and “unstable-surface dependency”.

# Maintenance & governance plan

- Track `rustc_public` documentation, the publishing MCP, and project-stable-mir release/process changes.
- Keep schemas compact and versioned independently of compiler internals.
- Maintain fixtures for stable support, partial support, semver-exempt leaks, and compiler-window drift.
- Publish guidance on composing workbench bundles with verification or spec-oriented evidence crates.

# Milestones

## 0.1
- `publicir.lock`
- one analyzer fixture schema
- one analysis receipt
- one tool compatibility matrix row

## 0.2
- normalized IR snapshots
- unstable-surface classification
- bundle diffing

## 1.0
- stable core schemas
- shared public fixture corpus
- multi-tool comparison helpers
- migration guidance for common `rustc_private`-to-`rustc_public` paths

# Open questions

- What is the smallest useful compatibility vocabulary across compiler version, `rustc_public` version, and bridge mode?
- Which semver-exempt surfaces deserve dedicated classes versus a generic “manual review” bucket?
- How much IR normalization is helpful before the workbench starts duplicating tool-specific logic?
- Which early adopter tools should shape the first shared corpus?

# Sources

- StableMIR / `rustc_public` goal: https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- GSoC 2025 results (`rustc_public` refactor, dual maintenance, compatibility tooling): https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Compiler-team MCP for publishing `rustc_public`: https://github.com/rust-lang/compiler-team/issues/949
- Rustc Librarification Project / project-stable-mir: https://github.com/rust-lang/project-stable-mir
- Current nightly `rustc_public` docs (public vs semver-exempt modules): https://doc.rust-lang.org/nightly/nightly-rustc/rustc_public/index.html
