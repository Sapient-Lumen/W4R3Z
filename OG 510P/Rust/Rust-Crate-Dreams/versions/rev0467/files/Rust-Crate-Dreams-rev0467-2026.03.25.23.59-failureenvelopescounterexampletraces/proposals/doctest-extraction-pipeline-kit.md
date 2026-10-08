---
id: P-0455
title: Doctest Extraction & Support Contract Kit — extracted manifests, rewrite lineage, execution-mode receipts, and docs-example support reports above rustdoc’s doctest substrate
status: idea
domains: [rustdoc, testing, docs, ci, cargo, cross-compilation, no_std, tooling]
last_reviewed: 2026-03-22
evidence:
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
  - https://doc.rust-lang.org/rustdoc/unstable-features.html#doctest
  - https://doc.rust-lang.org/beta/releases.html
  - https://doc.rust-lang.org/rustdoc/documentation-tests.html
  - https://rust-lang.github.io/rust-project-goals/2024h2/merged-doctests.html
---

# Problem

Rust documentation examples are no longer just prose blocks that happen to be exercised by `cargo test --doc`.

Current official substrate now makes several things concrete at once:

- the 2025 State of Rust survey says online documentation remains the preferred canonical reference;
- the Rust-for-Linux tooling goal explicitly asks for stable rustdoc features to extract and customize doctests;
- rustdoc already has an unstable `--output-format=doctest` JSON mode for machine-readable extraction;
- recent release notes stabilized `--test-runtool` / `--test-runtool-arg` and target-specific `ignore-*` doctest attributes;
- and merged-doctest work means execution grouping is now a meaningful part of semantics and performance.

That is meaningful substrate, but maintainers and downstream users still lack a boring workflow for questions like:

- which documentation examples actually exist and where did each one come from,
- what got rewritten or injected after extraction for a special environment,
- whether success came from standalone execution, merged execution, compile-only posture, ignore posture, or mere rendering,
- which examples are supported on host, target, wrapper-executed, docs.rs-rendered, or manual-review-only lanes,
- and how the support posture changed across toolchains, branches, or metadata policy changes.

The missing crate is not a replacement for rustdoc.
The missing crate is a **support-contract layer** that turns documentation examples into reviewable artifacts.

# What it provides

- `doctest-profile.toml` — extraction posture, rewrite policy, execution policy, and classification rules.
- `doctest.manifest.json` — extracted doctest metadata with source spans, block attributes, item paths, edition, and extraction provenance.
- `extraction-basis.receipt.json` — records which authority and output format produced the extracted manifest, including toolchain channel/version and rustdoc `format_version` where applicable.
- `rewrite-lineage.receipt.json` — records harness injections, environment-specific rewrites, hidden-setup handling, and rationale.
- `execution-mode.receipt.json` — records standalone vs merged vs wrapper vs compile-only vs ignored posture, runner basis, grouping basis, and caveats.
- `docs-example-support.report.json` — per-example support class across host run, target run, compile-only, render-only, ignored, and manual-review lanes.
- `grouping-comparison.report.json` — compares two bundles and classifies grouping, basis, target-scope, and attribute-scope comparability.
- `docs-example-drift.diff.json` — compares two bundles and classifies support shifts, rewrite shifts, extraction shifts, and grouping shifts.
- `doctest-support-bundle.manifest.json` — one portable manifest that keeps basis, rewrites, execution mode, support classes, imports, and drift separate.
- `cargo doctest-contract extract` — produce a manifest and optional extracted files.
- `cargo doctest-contract check` — emit execution-mode and support reports.
- `cargo doctest-contract diff <old> <new>` — compare docs-example posture across toolchains/configs.
- `*.doctestbundle.zip` — shareable artifact for CI, issue filing, or review handoff.

# What the crate should provide other people

1. **A boring machine-readable inventory** of docs examples.
2. **Rewrite honesty** when the environment mutates examples after extraction.
3. **Execution-basis honesty** when “the example ran” depends on grouping or wrappers.
4. **Support-class honesty** separating host execution, target execution, compile-only posture, ignore posture, and docs.rs rendering.
5. **Comparability honesty** when merged, standalone, cross-target, or attribute-sensitive runs should not be trended together casually.
6. **A diffable review artifact** for documentation-example drift.

# Persona / who it’s for

- maintainers with docs-heavy crates
- embedded / kernel / cross-target teams with custom runner needs
- release engineers gating documentation posture
- rustdoc contributors collecting reduced repro bundles
- downstream users who need to know whether an example is really supported

# Users & user stories

- **Maintainer**: “Extract every documentation example and show me which ones are really runnable versus render-only.”
- **Kernel or embedded maintainer**: “Record exactly what harness rewrites we applied and whether the examples ran under a wrapper or only compiled.”
- **Reviewer**: “Compare this branch against the last release and show whether support regressed because of ignore annotations, grouping mode, or runner policy.”
- **Rustdoc contributor**: “Attach one compact bundle that shows extraction output, grouping mode, and the execution posture we observed.”

# Prior art (and why it’s insufficient)

- `cargo test --doc` and rustdoc’s built-in doctest flow already exercise examples, but they do not leave a compact manifest + rewrite + support-class artifact.
- rustdoc’s unstable doctest JSON proves extraction is becoming machine-readable, but it is still too raw for ordinary review workflows.
- stable `--test-runtool` support proves wrapper-executed doctests matter, but does not record what those wrappers mean for support claims.
- docs.rs and coverage-oriented tooling matter, but they answer adjacent questions rather than the core support-contract question.

What remains missing is a **maintainer-facing contract layer** above those raw capabilities.

# Design goals

1. **Manifest-first** — examples should be inspectable before execution.
2. **Rewrite-explicit** — any environment-specific modification must be recorded.
3. **Execution-mode-visible** — standalone, merged, wrapper, compile-only, and ignore postures must remain visible.
4. **Support-class-conservative** — render-only/docs.rs success must never masquerade as execution.
5. **Adjacent-lane-friendly** — runner-profile, hosted-parity, and coverage tools should compose with this lane instead of being swallowed by it.

# MVP surface

- Minimal types: `DoctestManifest`, `RewriteLineageReceipt`, `ExecutionModeReceipt`, `DocsExampleSupportReport`, `DocsExampleDriftDiff`
- Minimal functions:
  - `extract_doctest_manifest()`
  - `record_rewrite_lineage()`
  - `capture_execution_mode()`
  - `build_docs_example_support_report()`
  - `diff_docs_example_bundles()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `custom-runners`
  - `nightly-doctest-json`
  - `markdown`

# Compatibility story

- Works above rustdoc; it should not invent a parallel Markdown parser when rustdoc extraction is available.
- Can start in a nightly-assisted extraction mode while keeping receipts explicit about that fact.
- Must preserve the difference between “as rustdoc extracted it”, “as our environment rewrote it”, and “as the runner executed it”.
- Should remain useful even when only manifest/support analysis is available and full execution is not.

# Conformance & fixtures

- Hidden-setup examples where custom harness injection must remain visible.
- Nightly rustdoc doctest JSON basis versus Markdown-fallback extraction authority.
- Same examples run standalone versus merged with different witness meaning.
- Host-run, cross-target, ignore-target, and docs.rs-render-only examples that need separate support classes.
- Drift fixtures where runner policy, grouping, or ignore annotations changed without prose changes.

# Path to boring stability

- Stabilize the artifact vocabulary first.
- Start with extraction + support classification before many runner adapters.
- Keep support classes conservative and easy to review.
- Treat docs.rs, runner profiles, and coverage as importable adjacent lanes rather than re-solving them here.

# Scorecard

- Impact: 4/5
- Novelty: 4/5
- Feasibility: 4/5
- Ecosystem breadth: 4/5
- Maintenance risk: 3/5
- Overall: **high-potential support-contract lane**
