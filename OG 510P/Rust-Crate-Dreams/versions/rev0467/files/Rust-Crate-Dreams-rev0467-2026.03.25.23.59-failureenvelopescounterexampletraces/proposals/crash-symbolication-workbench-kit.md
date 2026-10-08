---
id: P-0101
title: Crash Artifact & Symbolication Workbench Kit — capture receipts, module identity, symbol routes, and share-safe replayable crash bundles
status: idea
domains: [devtools, reliability, observability, debugging, interoperability, crash-reporting]
last_reviewed: 2026-03-21
evidence:
  - https://github.com/rust-minidump/rust-minidump
  - https://github.com/rust-minidump/rust-minidump/blob/main/minidump-stackwalk/README.md
  - https://github.com/rust-minidump/rust-minidump/blob/main/RELEASES.md
  - https://docs.rs/wholesym/latest/wholesym/
  - https://docs.rs/symbolic/latest
  - https://docs.rs/minidumper/latest/minidumper/
  - https://github.com/rust-minidump/minidump-writer
  - https://hacks.mozilla.org/2022/06/everything-is-broken-shipping-rust-minidump-at-mozilla/
  - https://jake-shadle.github.io/crash-reporting/
  - https://chromium.googlesource.com/breakpad/breakpad/%2B/master/docs/symbol_files.md
---

# Problem

Rust applications increasingly ship cross-platform, but crash triage is still too often a glue-script lane:

- one system captures a minidump or crash attachment,
- another tool guesses which modules were present,
- a symbol server or local cache resolves debug info if it can,
- and a support engineer still has to ask whether the symbol files matched, whether the report was produced offline, whether memory was redacted, and whether another team can replay the analysis.

Current Rust substrate is now strong enough that the missing layer is more specific than “Rust needs crash reporting.”

- `rust-minidump` provides parsing and analysis for minidumps, with `minidump-processor` and `minidump-stackwalk` as the rich analysis path.
- `minidump-stackwalk` can use Breakpad symbols, Tecken-style symbol servers, native debuginfo, and direct symbol-file inputs.
- `wholesym` now provides fast native-debug-info lookup across Windows, macOS, and Linux with symbol servers, local debug files, and Breakpad sources.
- `symbolic` still provides broad symbolication substrate and multiple debug-info formats.
- `minidumper` and `minidump-writer` provide capture-side substrate for out-of-process monitor models.
- Mozilla’s deployment notes and release history show that reliability hardening, fuzzing, soft-error reporting, symbol stats, and debug-id/code-id nuances all matter in practice.

What remains missing is one boring, receiver-facing support contract that answers:

1. **How was this crash captured?**
2. **Which module identities are authoritative for symbol lookup?**
3. **Which symbol sources were allowed and in what order?**
4. **How complete and trustworthy was the analysis result?**
5. **Can another team replay this report deterministically?**
6. **Is this bundle actually safe to share?**

The worthy crate is therefore **not** another crash collector, **not** another hosted crash service, and **not** just another stackwalker.
It is a **Crash Artifact & Symbolication Workbench Kit**: a crate family and CLI that helps teams author, check, diff, and bundle the support contract around real Rust crash artifacts.

# Main judgment

A worthy crate contribution here should provide a reviewable contract over five distinct truths plus a bundle manifest:

1. **capture basis** — in-process, external monitor, imported OS artifact, test harness, or manual review.
2. **module identity** — module path/name, load base/size, debug-id/code-id/build-id posture, and provenance lineage.
3. **symbol route** — local cache, bundled Breakpad symbols, native debuginfo, symbol server, fallback order, timeout posture, and offline/online mode.
4. **analysis coverage + determinism** — missing/corrupt symbol counts, soft errors, stackwalk engine version, replay basis, and whether the output is stable without re-fetching artifacts.
5. **share-safety posture** — raw memory, paths, usernames, environment fragments, source locations, symbol inclusion, and redaction receipts.
6. **bundle manifest** — how the captured dump, receipts, symbols, reports, and notes fit together.

That contract is more valuable than leaving downstream users to reconstruct crash provenance from issue threads, symbol-cache state, and whatever one-off files happened to be attached to a bug.

# What it provides

- `crash-bundle.toml` — maintainer or incident-author declaration of capture posture, symbol policy, and redaction policy.
- `capture-basis.receipt.json` — records whether the crash came from in-process capture, out-of-process monitor capture, imported artifact, or synthetic/test input.
- `module-identity.receipt.json` — normalized module table with name, code file, base, size, debug-id/code-id/build-id posture, and identity confidence.
- `symbol-route.receipt.json` — ordered symbol sources, offline/online mode, timeouts, cache paths, and fallback decisions.
- `analysis-coverage.report.json` — counts for loaded/missing/corrupt symbols, soft errors, inline-frame posture, and unresolved-frame classes.
- `report-determinism.receipt.json` — whether the stackwalk/report can be reproduced from only bundled artifacts, or still depends on live network/system state.
- `share-safety.receipt.json` — what was redacted, stripped, left intact, or marked manual-review-only.
- `crash-bundle.manifest.json` — portable manifest tying receipts, dump files, symbol material, rendered reports, and notes together.
- `crash-diff.report.json` — compares two bundles or two analysis runs and classifies `module_identity_changed`, `symbol_source_changed`, `coverage_changed`, `replayability_changed`, `share_safety_changed`, and `manual_review_required`.
- `crash-notes.summary.md` — short human-facing explanation of what another reviewer can trust.
- `cargo crashworkbench capture` — create receipts and manifest from a crash artifact.
- `cargo crashworkbench doctor` — verify module identity, symbol-route, replayability, and share-safety posture.
- `cargo crashworkbench diff` — compare two crash bundles or two reports.
- `cargo crashworkbench bundle` — produce one compact portable bundle for another team.

# What the crate should provide other people

1. **One capture receipt** instead of asking whether the dump was written in-process, by a monitor process, or imported from elsewhere.
2. **One module-identity answer** instead of ad hoc debug-id/code-id/build-id guessing.
3. **One symbol-route receipt** instead of folklore about symbol servers, caches, or local debug files.
4. **One coverage report** that says whether a pretty stack trace is actually well-supported or mostly unresolved.
5. **One replayability/determinism answer** instead of “it worked on my symbol cache.”
6. **One share-safety receipt** instead of hand-wavy “we redacted the sensitive bits.”
7. **One compact manifest** that other tools and support teams can ingest.
8. **One diffable artifact set** so crash-processing drift across releases or tooling changes becomes reviewable.

# Persona / who it’s for

- app teams shipping cross-platform Rust binaries
- SDK/runtime teams operating crash pipelines
- support and incident engineers who need portable artifacts
- maintainers of desktop, mobile, CLI, embedded-hosted, and game/tooling apps
- docs/tool authors who want stable crash bundle vocabulary instead of one-off upload conventions

# Users & user stories

- **Desktop app maintainer**: “Hand another team one bundle that says which dump we captured, which symbols matched, and whether they can replay the report offline.”
- **Support engineer**: “See immediately whether a missing frame is because symbols were absent, corrupt, or never fetched.”
- **Security reviewer**: “Check one receipt that says whether raw memory, usernames, source paths, or symbol files are included.”
- **Release engineer**: “Diff two crash-analysis runs and learn whether a toolchain or symbol-route change altered the stackwalk.”
- **Library/tool author**: “Integrate minidump capture and symbolication substrate without inventing a private bundle format.”

# Prior art (and why it’s insufficient)

- `rust-minidump` provides parsing and analysis, but not a shared support contract for replayability, redaction posture, or bundle shape.
- `minidump-stackwalk` provides rich output, current soft-error reporting, symbol stats, native-debug-info support, and symbol-server integration.
- `wholesym` and `symbolic` provide powerful symbol-resolution substrate across native formats and Breakpad symbols.
- `minidumper` and `minidump-writer` provide capture-side substrate.
- Mozilla’s deployment and fuzzing work prove that robust minidump analysis requires explicit hardening and artifact discipline.
- Breakpad symbol files provide a common text symbol format, but not the receiver-facing workflow contract above capture, routing, coverage, and redaction.

What remains missing is the joined artifact layer that says:

- this is how the dump was captured,
- this is the authoritative module identity set,
- this is the symbol source route we allowed,
- this is how complete and replayable the analysis really was,
- and this is what is safe to share.

That is a different lane from:

- **P-0073** async replay/debugging,
- debugger UX / visualizer lanes,
- desktop shipkits,
- hosted crash dashboards,
- or generic evidence-bundle substrate.

# Design goals

1. **Artifact-first** — bundles and receipts are the unit of collaboration.
2. **Identity honesty** — keep debug-id/code-id/build-id posture explicit.
3. **Route honesty** — keep local/native/server symbol routes explicit.
4. **Coverage honesty** — make missing/corrupt/unresolved symbol states first-class.
5. **Replayability honesty** — tell people whether a report can really be reproduced offline.
6. **Share-safety first** — redaction and included sensitive material must be reviewable.
7. **Join, don’t replace** — sit above existing capture and symbolication substrate.

# MVP surface

- Minimal `crash-bundle.toml` schema with capture mode, symbol policy, and redaction policy.
- `capture-basis.receipt.json`, `module-identity.receipt.json`, `symbol-route.receipt.json`, `analysis-coverage.report.json`, `report-determinism.receipt.json`, `share-safety.receipt.json`, and `crash-bundle.manifest.json`.
- `cargo crashworkbench doctor` warnings for identity mismatch, missing symbols, non-replayable network routes, and unsafe-share bundles.
- `crash-diff.report.json` to compare two crash bundle analyses.
- `cargo crashworkbench summary` to render a concise Markdown review note.

# Distinctive implementation shape

## Crates

- `crashworkbench-model` — schemas, summaries, diff logic, and receipt vocabularies.
- `crashworkbench-capture-import` — adapters for `minidumper`, `minidump-writer`, imported artifacts, and synthetic fixtures.
- `crashworkbench-symbol-route` — adapters for Breakpad/native/`wholesym`/server route descriptions.
- `crashworkbench-doctor` — identity checks, coverage checks, replayability checks, and share-safety checks.
- `cargo-crashworkbench` — CLI.

## Commands

- `cargo crashworkbench capture`
- `cargo crashworkbench doctor`
- `cargo crashworkbench diff`
- `cargo crashworkbench summary`
- `cargo crashworkbench bundle`

# Conformance & fixtures

- external monitor capture with stack sanitization
- debug-id present vs code-id fallback for Windows modules
- offline Breakpad bundle with frozen symbol inputs
- live symbol server route with unresolved replayability
- native-debuginfo plus Breakpad mixed route coverage
- safe-share bundle with stripped memory and path redaction

# Path to boring stability

- Stabilize the receipts and manifest before adding hosted integrations or viewers.
- Treat `manual_review_required` as a first-class honest outcome.
- Prefer import adapters for existing capture/symbolication tools over private parsers and uploaders.
- Keep share-safety and replayability explicit even when the stack trace looks good.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A crate family that ingests a minidump or imported crash artifact, emits capture / module-identity / symbol-route / coverage / replayability / share-safety receipts plus a compact manifest, and lets another team tell whether the resulting stackwalk is reproducible and safe to share.

# De-risk plan

1. Keep `0.1` focused on receipts and manifest shape, not dashboards or crash collection.
2. Import current substrate instead of replacing it.
3. Make identity mismatch, symbol gaps, and replayability loss first-class doctor outcomes.
4. Keep network routes optional and frozen-cache workflows easy.

# Non-goals

- Not a hosted crash-reporting service.
- Not a replacement for Breakpad, Crashpad, or Sentry-style collection stacks.
- Not a universal debugger UI.
- Not a promise to automatically remove all sensitive data.

# Architecture & API sketch

```rust
pub fn capture_basis(input: &CrashInput) -> Result<CaptureBasisReceipt>;
pub fn capture_module_identity(input: &CrashInput) -> Result<ModuleIdentityReceipt>;
pub fn capture_symbol_route(input: &CrashInput) -> Result<SymbolRouteReceipt>;
pub fn analyze_coverage(input: &CrashInput) -> Result<AnalysisCoverageReport>;
pub fn capture_report_determinism(input: &CrashInput) -> Result<ReportDeterminismReceipt>;
pub fn capture_share_safety(input: &CrashInput) -> Result<ShareSafetyReceipt>;
pub fn doctor_bundle(bundle: &CrashBundle) -> Result<CrashDoctorReport>;
pub fn write_bundle(bundle: &CrashBundle, out: &Path) -> Result<()>;
```

# Security / safety model

- Treat crash bundles and dump files as untrusted input.
- Bound file sizes, decompression, and symbol-fetch behavior.
- Make included memory, source paths, usernames, and symbol files explicit in share-safety receipts.
- Default to offline-first replay when possible.

# Maintenance & governance plan

- Version the receipt schemas carefully.
- Keep adapters modular for `rust-minidump`, `wholesym`, `symbolic`, and capture-side crates.
- Maintain a public redacted fixture corpus.
- Keep this lane distinct from generic evidence-bundle substrate and hosted crash platforms.

# Milestones

## 0.1
- receipts and manifest
- doctor checks
- summary rendering
- small fixture corpus

## 0.2
- diff support
- more adapters for symbol routes and capture sources
- optional HTML or richer rendered summaries

## 1.0
- stable artifact core
- explicit compatibility guidance for existing crash stacks
- importer matrix and governance docs

# Open questions

- How much of symbol-cache contents should the bundle capture versus reference externally?
- Which defaults should safe-share mode choose for source paths and raw memory slices?
- How should native debug-info routes and Breakpad routes be normalized when both are available?
