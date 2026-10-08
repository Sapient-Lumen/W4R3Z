---
id: P-0476
title: Rustdoc Coverage Review Bundle Kit — coverage snapshots, API-surface debt ledgers, example-coverage diffs, and docs-regression receipts
status: idea
domains: [rustdoc, documentation, cargo, ci, library-maintenance, devtools]
last_reviewed: 2026-03-07
evidence:
  - https://doc.rust-lang.org/rustdoc/unstable-features.html
  - https://doc.rust-lang.org/cargo/commands/cargo-rustdoc.html
  - https://doc.rust-lang.org/nightly/nightly-rustc/rustdoc_json_types/
  - https://rust-lang.github.io/rfcs/2963-rustdoc-json.html
---

# Problem

Rust increasingly has real substrate for documentation analysis:

- `rustdoc --show-coverage` can emit machine-readable JSON coverage data,
- `cargo rustdoc` can emit rustdoc JSON on nightly,
- `rustdoc_json_types` exposes the public API for that JSON surface,
- and the classic `missing_docs` / private-docs lint path already gives maintainers raw warning signals.

But ordinary library teams still do not have a boring answer to questions like:

- which **public API changes** created documentation debt,
- whether a release candidate lost docs on high-value items or only on obscure internal ones,
- which examples disappeared versus which prose disappeared,
- how reexports or generated APIs distorted the raw file-level percentages,
- and how to attach one compact artifact to a docs PR, release review, or docs sprint planning meeting.

Today the workflow is still fragmented:

- run `missing_docs` and read warning spam,
- maybe run `rustdoc --show-coverage` and stare at file totals,
- maybe parse rustdoc JSON with bespoke tooling,
- then manually reconstruct which changes actually matter for users.

That means the missing crate is not another docs host.

The missing crate is a **rustdoc coverage review bundle kit**: a crate and cargo subcommand that join coverage facts, rustdoc JSON surface facts, and release-review diffs into one compact artifact.

# What it provides

- `docs-coverage-profile.toml` — pins toolchain, capture mode, weighting policy, public/private scope, and redaction options.
- `docs-coverage.raw.json` — normalized `--show-coverage` results plus example-coverage facts.
- `api-docs.ledger.json` — public-item ledger derived from rustdoc JSON with doc presence, example presence, reexport status, stability/deprecation tags when visible, and coarse importance buckets.
- `docs-hotspots.report.json` — prioritized documentation debt grouped by public surface, changed items, modules, or owners.
- `docs-coverage.diff.json` — compare two runs and classify regressions, improvements, churn from reexports, and coverage-only noise.
- `cargo docs-coverage capture` — emit one reviewable docs-coverage bundle.
- `cargo docs-coverage diff <old> <new>` — compare documentation posture across commits, branches, or releases.
- `cargo docs-coverage doctor` — flag suspiciously misleading totals, missing rustdoc JSON, mixed-toolchain captures, or generated-API blind spots.
- `*.doccoverbundle.zip` — portable artifact for CI, docs triage, release review, or upstream issue filing.

# What the crate should provide other people

1. **A boring documentation review artifact** above rustdoc’s raw coverage output.
2. **An API-aware docs debt ledger** instead of only per-file percentages.
3. **A diffable release check** when public docs or examples regress.
4. **A prioritization surface** for docs work that distinguishes public/high-impact debt from noisy internal debt.
5. **A bridge** between `--show-coverage`, rustdoc JSON, and maintainer-facing docs workflows.

# Persona / who it’s for

- maintainers of public libraries and SDKs
- workspace owners running documentation debt sprints
- CI/release engineers wanting docs regression gates
- docs/tooling authors who need one stable artifact instead of bespoke joins

# Users & user stories

- **Library maintainer**: “Show me whether this release candidate reduced docs quality on the public API that users actually touch.”
- **Docs lead**: “Give me one ledger of undocumented or example-poor items prioritized by impact, not just file percentages.”
- **Reviewer**: “Attach one diffable bundle to the PR proving what documentation regressed.”
- **Tooling author**: “Consume one artifact instead of separately parsing coverage output, lint output, and rustdoc JSON.”

# Prior art (and why it’s insufficient)

- `missing_docs` and related lints find undocumented items, but they do not leave behind a compact review bundle.
- `--show-coverage` reports totals and can emit JSON, but the output is still mostly a raw measurement surface rather than an API-aware triage artifact.
- rustdoc JSON is explicitly intended to power other tools and front-ends, but it is still too low-level for ordinary docs maintenance workflows.

What remains missing is a **coverage + API-surface + diff bundle** that turns documentation maintenance into a routine review habit.

# Design goals

1. **Review-first** — optimize for PRs, release signoff, and docs planning, not dashboards.
2. **API-aware** — public-item importance must be visible instead of hidden behind file percentages.
3. **Examples-visible** — prose and code-example debt should be separable.
4. **Diff-friendly** — regressions and improvements must be easy to compare.
5. **Nightly-honest** — keep toolchain/version facts explicit when richer rustdoc data depends on nightly.

# MVP surface

- Minimal types: `DocsCoverageProfile`, `CoverageSnapshot`, `ApiDocsLedger`, `DocsHotspotsReport`, `DocsCoverageDiff`, `DocsCoverageBundle`
- Minimal functions:
  - `capture_docs_coverage_bundle()`
  - `normalize_show_coverage_output()`
  - `build_api_docs_ledger()`
  - `diff_docs_coverage_bundles()`
  - `run_docs_coverage_doctor()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `nightly-rustdoc`
  - `markdown`
  - `owners`

# Compatibility story

- Full-fidelity mode should target nightly because rustdoc JSON and richer coverage workflows remain nightly-oriented.
- A reduced mode can still import lint/coverage output without the full API ledger.
- Bundles must preserve which facts came from raw coverage JSON, which came from rustdoc JSON, and which were inferred conservatively.
- The crate should remain useful even if upstream stabilizes more docs-analysis surfaces, because the review/diff bundle still matters.

# Conformance & fixtures

- One fixture with public reexports where raw file totals would mislead.
- One fixture with excellent prose docs but poor example coverage.
- One fixture with generated or macro-heavy API surface.
- One fixture with a small public regression that should be ranked above larger internal churn.
- Goldens for `public_regression`, `example_regression`, `reexport_noise`, and `manual_review_required`.

# Path to boring stability

- Stabilize the bundle schema before adding dashboards or ownership integrations.
- Start with capture/diff/hotspots instead of broad docs scoring theory.
- Keep weighting categories coarse and reviewable.
- Prefer explicit uncertainty over pretending rustdoc already exposes perfect semantic importance.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that capture rustdoc coverage JSON plus rustdoc JSON surface facts, build a public-item documentation ledger, and emit one diffable docs-review bundle.

# De-risk plan

1. Start with capture/diff/prioritization before trying to score docs quality too deeply.
2. Keep the first importance model simple: changed public items, examples, reexports, and deprecations.
3. Validate on one crate with dense public API and one workspace with mixed internal/public modules.
4. Treat macro-generated items and reexports as first-class uncertainty sources.

# Non-goals

- Not a replacement for rustdoc or docs.rs.
- Not a generalized documentation site.
- Not a promise that documentation quality can be reduced to one universal score.
- Not another generic lint runner.

# Architecture & API sketch

```rust
pub struct DocsDebtHotspot {
    pub item_path: String,
    pub public_api: bool,
    pub missing_docs: bool,
    pub missing_examples: bool,
    pub priority: String,
}

pub fn capture_docs_coverage_bundle(root: &Path) -> Result<DocsCoverageBundle>;
pub fn normalize_show_coverage_output(raw: &str) -> Result<CoverageSnapshot>;
pub fn build_api_docs_ledger(bundle: &DocsCoverageBundle) -> Result<ApiDocsLedger>;
pub fn diff_docs_coverage_bundles(old: &DocsCoverageBundle, new: &DocsCoverageBundle) -> DocsCoverageDiff;
```

Bundle draft: `docs-coverage-profile.toml`, `docs-coverage.raw.json`, `api-docs.ledger.json`, `docs-hotspots.report.json`, `docs-coverage.diff.json`, `notes.md`.

# Security / safety model

- Treat rustdoc output as untrusted input and parse defensively.
- Support redaction of local paths or unpublished crate names in exported bundles.
- Keep toolchain/version facts prominent so mixed-nightly runs are not confused with apples-to-apples comparisons.
- Never pretend file-level coverage percentages fully capture user-facing documentation quality.

# Maintenance & governance plan

- Track rustdoc coverage output, rustdoc JSON format changes, and stabilization progress closely.
- Keep schemas compact and versioned.
- Maintain fixtures for reexports, examples, macro-heavy APIs, and mixed public/private workspaces.
- Publish guidance on when docs regression gates should be advisory versus blocking.

# Milestones

## 0.1
- capture raw coverage JSON
- build public API docs ledger
- export bundle

## 0.2
- bundle diffing
- hotspot prioritization
- basic CI adapter

## 1.0
- stable bundle schema
- curated docs-maintenance corpus
- upstream issue-template integration

# Open questions

- What is the smallest useful importance vocabulary for public API documentation debt?
- How should reexports, blanket impls, and generated APIs influence prioritization?
- Which docs/example regressions are stable enough to gate in CI without creating noise?

# Sources

- rustdoc unstable features (`--show-coverage`, JSON output): https://doc.rust-lang.org/rustdoc/unstable-features.html
- `cargo rustdoc` output options: https://doc.rust-lang.org/cargo/commands/cargo-rustdoc.html
- `rustdoc_json_types` public API: https://doc.rust-lang.org/nightly/nightly-rustc/rustdoc_json_types/
- RFC 2963 rustdoc JSON: https://rust-lang.github.io/rfcs/2963-rustdoc-json.html
