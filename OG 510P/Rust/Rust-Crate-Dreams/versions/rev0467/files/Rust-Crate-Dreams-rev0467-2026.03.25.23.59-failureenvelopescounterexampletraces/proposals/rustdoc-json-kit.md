---
id: P-0051
title: Rustdoc JSON Support Contract Kit — source-route receipts, format-window matrices, and normalization-loss reports
status: idea
domains: [docs, rustdoc, tooling, api, semver, cargo, docsrs]
last_reviewed: 2026-03-23
evidence:
  - https://doc.rust-lang.org/rustdoc/unstable-features.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://docs.rs/about/rustdoc-json
  - https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
---

# Problem

Rustdoc JSON is no longer obscure substrate.
It now sits under semver checking, API search/indexing, alternate documentation frontends, crate knowledge packs, and increasingly machine-facing support workflows.
At the same time, the ecosystem still lacks one boring crate that says:

- **where a given JSON blob came from**, 
- **which format-version / toolchain windows a consumer actually supports**,
- **what information was normalized or dropped on the floor**,
- and **which stronger downstream claims still require manual review**.

That gap is sharper now because official sources have become much more explicit:

- rustdoc still documents `--output-format json` as an **experimental** format behind unstable options;
- Cargo still documents `output-format` for `cargo rustdoc` as an **unstable** feature;
- docs.rs now hosts rustdoc JSON directly, warns consumers to inspect `format_version`, keeps older format versions around after rebuilds, and notes that releases before 2025-05-23 may not have downloadable JSON until rebuild coverage reaches them;
- the cargo-semver-checks goal explicitly says rustdoc JSON is still nightly-only and unstable, but also shows that one tool can support a **range of formats** at once;
- that same goal also documents important blind spots: target-package rustdoc JSON alone does not settle cross-crate reexports, and manifest-only SemVer changes are not present in rustdoc JSON at all;
- and the 2025 State of Rust survey says online documentation remains the preferred canonical reference, which increases the value of good machine-consumable documentation substrate.

So the missing crate is no longer just “a parser for rustdoc JSON.”

The sharper missing crate is a **rustdoc JSON support contract kit**: a crate that can generate or import rustdoc JSON, normalize it into a stable intermediate model, and emit reviewable artifacts for **source route**, **format support windows**, **normalization loss**, and **portable handoff**.

# 2026-03-23 implementation refresh — route truth, version windows, and loss honesty

The current archive already knew that P-0051 should generate, cache, and normalize rustdoc JSON.
What it did **not** yet make reviewable enough was the difference between:

1. **source route** — local nightly generation, docs.rs import, rustup `rust-docs-json` component import for toolchain crates, or manual file import;
2. **format window** — which `format_version` values, toolchain windows, or parser adapters are truly supported by the consumer;
3. **normalization loss** — which item kinds, cross-crate edges, manifest facts, or metadata fields are missing, deferred, or intentionally not represented in the normalized IR;
4. **claim ceiling** — where downstream tools should stop saying “supported” and instead say “manual review required.”

A worthy implementation should therefore promote four first-class receiver-facing artifacts:

- `source-route.receipt.json`
- `format-window.matrix.json`
- `normalization-loss.report.json`
- `rustdoc-json-support-bundle.manifest.json`

This keeps P-0051 from collapsing into either:

- another single-version parser,
- another docs.rs scraper,
- another semver-check wrapper,
- or a fake promise that “we have normalized rustdoc JSON” means every downstream query is safe.

# What it provides

Working build sketch: `meta/rustdoc-json-version-window-plan-2026-03-23.md`.

- `rustdoc-json-profile.toml` — declares generation/import policy, cache keys, supported format windows, and normalization strictness.
- `source-route.receipt.json` — records whether JSON came from local `cargo rustdoc`, direct `rustdoc`, docs.rs download, rustup `rust-docs-json`, or manual file import, plus target/toolchain/format observations.
- `format-window.matrix.json` — records supported `format_version` values, toolchain windows, adapter classes, and support levels (`native`, `translated`, `legacy-import-only`, `unsupported`).
- `normalization-loss.report.json` — records what was omitted, downgraded, unresolved, or intentionally left out of the normalized IR.
- `normalized-crate.json` — stable intermediate representation for public API and related query surfaces.
- `query-surface.report.json` — optional consumer-facing note for which normalized queries are considered stable above the current IR.
- `cache-entry.receipt.json` — exact cache key basis: source route, crate identity, toolchain, target, features, rustdoc flags, and `format_version`.
- `support-drift.diff.json` — compare old/new source routes, format windows, and normalization-loss posture.
- `cargo rustdoc-json-kit capture` — generate or import a bundle.
- `cargo rustdoc-json-kit diff <old> <new>` — compare two support bundles or two normalized IR captures.
- `cargo rustdoc-json-kit doctor` — warn when a requested query or downstream consumer outruns the admitted support window or loss profile.
- `*.rustdocjsonbundle.zip` — portable handoff for other tools and reviewers.

# What the crate should provide other people

1. **One exact source-route receipt** instead of vague “this came from rustdoc somewhere” language.
2. **A stable support-window vocabulary** for format versions and toolchain spans.
3. **Normalization-loss honesty** so missing cross-crate edges, omitted manifest facts, or downgraded attributes remain explicit.
4. **A reusable normalized IR** for public API and docs-facing tooling.
5. **Portable review bundles** for semver tools, docs frontends, and assistant-facing pack builders.
6. **A diff story** so support windows and loss surfaces do not drift silently.
7. **A conservative ceiling** on downstream claims when the imported JSON route or current format window is not enough.

# Persona / who it’s for

- tool authors building on rustdoc JSON
- maintainers of semver, API-diff, and docs-analysis tools
- docs and search front-end authors
- CI/release engineers archiving API evidence
- crate-knowledge / LLM-pack builders who need exact rustdoc JSON provenance

# Users & user stories

- **Semver-tool maintainer**: “Tell me whether this old docs.rs JSON is inside my supported format window and what I will lose if I normalize it.”
- **Docs frontend author**: “Give me one stable IR and one explicit loss report instead of making me reverse-engineer every rustdoc JSON version.”
- **CI owner**: “Archive one bundle that says how the JSON was obtained, which version it used, and what our parser admitted.”
- **Knowledge-pack builder**: “Import rustdoc JSON without pretending docs.rs latest, local nightly generation, and rustup toolchain JSON are interchangeable.”

# Prior art (and why it’s insufficient)

- `rustdoc_types` and related type crates describe raw rustdoc JSON structures, but they do not by themselves export a cross-version support contract.
- Cargo and rustdoc expose experimental JSON generation, but that is generation substrate rather than a stable compatibility story.
- docs.rs hosts downloadable rustdoc JSON, but explicitly warns that `format_version` matters and that older releases may still be missing coverage.
- cargo-semver-checks proves that multi-version support is possible, but its compatibility logic is not yet the ecosystem’s general-purpose shared review layer.
- crate-knowledge and docs.rs parity ideas in this archive sit *above* the raw rustdoc JSON layer and should not have to silently re-solve it.

What remains missing is the **joined support artifact** above these pieces: one thing another engineer can inspect to answer “where did the JSON come from, what versions are supported, what was lost, and how far can I trust downstream conclusions?”

# Design goals

1. **Support-contract-first** — reviewable receipts and loss honesty before fancy queries.
2. **Route explicitness** — local nightly generation, docs.rs import, rustup component import, and manual file import must stay distinct.
3. **Version-window explicitness** — supported `format_version` spans must be machine-readable.
4. **Loss explicitness** — the normalized IR must say what it cannot represent.
5. **Reuse-first** — other tools should be able to consume the bundle without re-running rustdoc.
6. **Diffability** — support windows and normalization behavior must be comparable over time.
7. **Conservative ceilings** — unsupported lanes should stay manual-review territory instead of being guessed away.

# Non-goals

- Replacing rustdoc.
- Stabilizing rustdoc JSON itself.
- Claiming that every downstream query can be answered from rustdoc JSON alone.
- Reimplementing semver policy or docs.rs build parity inside this crate.

# Architecture & API sketch

- `rustdoc-json-kit` library:
  - `capture_source_route(...) -> SourceRouteReceipt`
  - `import_docsrs_json(...) -> SourceRouteReceipt`
  - `load_raw(...) -> RawRustdocJson`
  - `normalize(raw, support_window) -> (NormalizedCrate, NormalizationLossReport)`
  - `compute_format_window(...) -> FormatWindowMatrix`
  - `diff_support_bundles(old, new) -> SupportDriftDiff`
- CLI:
  - `cargo rustdoc-json-kit capture`
  - `cargo rustdoc-json-kit import-docsrs`
  - `cargo rustdoc-json-kit doctor`
  - `cargo rustdoc-json-kit diff`
- Caching:
  - key = `(source route, crate identity, toolchain, target, features, rustdoc flags, format_version)`
  - content-addressed files with retained receipts/loss reports.

# Compatibility story

- Works for local nightly generation and imported docs.rs artifacts first.
- Keeps rustup `rust-docs-json` for toolchain crates separate from project-local crate generation.
- Must preserve `format_version`, target, and route metadata even when a later normalized IR erases those distinctions.
- Should remain useful even as format versions evolve, because the format window and loss report tell other tools how much is still supported.

# Conformance & fixtures

- One fixture where docs.rs import is available but only for newer releases because older rebuild coverage is absent.
- One fixture where the tool consumes multiple `format_version` values through adapters but admits different support levels.
- One fixture where cross-crate reexports remain unresolved without importing additional JSON artifacts.
- One fixture where manifest-only SemVer questions remain out of scope for rustdoc JSON normalization.
- One fixture where toolchain-crate JSON comes from `rust-docs-json` and must not be confused with local crate generation.
- One fixture where the normalized IR keeps path/item queries but explicitly downgrades unsupported relations.

# Path to boring stability

- Stabilize route receipts and format-window/loss schemas before broadening the query DSL.
- Start with public API / item graph normalization and conservative loss categories.
- Treat cross-crate and manifest-aware enrichment as explicit extensions rather than default magic.
- Keep docs.rs import optional and provenance-heavy.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 5/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that can either generate or import rustdoc JSON, emit a route receipt, declare supported format windows, normalize into one stable IR, and attach a loss report explaining what the IR still does not prove.

# De-risk plan

1. Start with route receipt + format window + loss report before ambitious query language work.
2. Use current official rustdoc/Cargo/docs.rs statements as the initial truth source for route classes and version honesty.
3. Validate on one docs.rs-imported crate, one locally generated nightly crate, and one `rust-docs-json` toolchain-crate lane.
4. Keep the first loss taxonomy small: unresolved cross-crate items, omitted manifest facts, unsupported raw fields, and intentionally downgraded relations.

# Open questions

- Should docs.rs download support live in the core crate or an optional adapter?
- Which normalized queries are mature enough for `0.1` promises?
- How should the crate distinguish “can parse” from “can answer downstream support questions safely”?
- When should the crate recommend importing multiple rustdoc JSON blobs for cross-crate analysis rather than reporting loss?

# Sources

See front matter links.
