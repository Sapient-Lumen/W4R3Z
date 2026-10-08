---
id: P-0472
title: Docs.rs Build Parity & Evidence Kit — docs.rs preflight receipts, sandbox-limit reports, and local-vs-hosted diff bundles
status: idea
domains: [docs, rustdoc, docsrs, cargo, ci, release-engineering, devtools]
last_reviewed: 2026-03-17
evidence:
  - https://docs.rs/about/builds
  - https://docs.rs/about/metadata
  - https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
  - https://github.com/rust-lang/docs.rs
  - https://crates.io/crates/cargo-docs-rs
---

# Problem

Rust now has real substrate for docs.rs-facing documentation workflows:

- docs.rs documents its current nightly toolchain, sandbox limits, target behavior, `docsrs`/`DOCS_RS` signals, and `package.metadata.docs.rs` knobs,
- docs.rs explicitly recommends adding `cargo docs-rs` to CI when using docs.rs metadata or `#[cfg(docsrs)]`,
- docs.rs explains that the `docsrs` cfg only applies to the final rustdoc invocation and not to dependencies or workspace crates,
- docs.rs explains that every target except `x86_64-unknown-linux-gnu` is cross-compiled,
- and the docs.rs repository documents how to reproduce the hosted build environment locally with the builder.

The same docs also make the missing layer obvious:

- `cargo docs-rs` is helpful, but docs.rs explicitly says it does **not** perfectly replicate the hosted environment,
- hosted docs.rs builds have special limits and a moving nightly toolchain,
- the default target list changed in October 2025, so crate owners can drift just by leaving docs posture implicit,
- build failures often depend on target count, read-only filesystem assumptions, missing native dependencies, or build-log truncation,
- and maintainers still lack one compact artifact they can attach to CI, release review, or upstream docs.rs issues.

So the missing crate is not “yet another way to run rustdoc.”

The missing crate is a **docs.rs parity and evidence kit**: a Cargo-adjacent crate that captures what we tried, how close it was to docs.rs, what limits/configuration mattered, and how local and hosted results differed.

# What it provides

- `docsrs-profile.toml` — pins docs.rs metadata interpretation, selected targets, feature policy, replay mode, and redaction behavior.
- `docsrs-env.receipt.json` — records Cargo/rustc/rustdoc versions, known docs.rs nightly/build-image facts, `DOCS_RS`/`docsrs` assumptions, and local host details.
- `docsrs-config.report.json` — normalized view of `[package.metadata.docs.rs]`, effective `default-target`, `targets`, `additional-targets`, feature flags, rustdoc args, and cargo args.
- `docsrs-limit.report.json` — resource/limit facts that may matter for parity, such as target count, read-only-path expectations, current documented RAM / time / log-size constraints, and network assumptions.
- `docsrs-results.json` — normalized success/failure outcomes plus extracted diagnostics and phase boundaries.
- `preflight-fidelity.report.json` — classifies whether the evidence is metadata-only, local preflight, builder-local reproduction, hosted import, or a joined bundle.
- `hosted-build-import.receipt.json` — imported docs.rs build-summary / build-log facts with explicit truncation posture.
- `drift-cause.report.json` — normalized candidate causes that explain hosted-vs-local divergence without flattening uncertainty.
- `docsrs-diff.json` — compare two runs or compare local preflight results against hosted docs.rs build facts when available.
- `cargo docsrs-evidence capture` — run a local preflight and emit a reviewable bundle.
- `cargo docsrs-evidence diff <old> <new>` — compare docs.rs-facing documentation posture across toolchains, branches, or metadata changes.
- `cargo docsrs-evidence explain` — summarize why the run diverged from docs.rs assumptions.
- `*.docsrsbundle.zip` — portable artifact for issue filing, CI debugging, release review, or support handoff.

# What the crate should provide other people

1. **A boring docs.rs preflight receipt** above `cargo rustdoc` and `cargo docs-rs`.
2. **Fidelity honesty** about whether the evidence came from metadata analysis, local preflight, local builder reproduction, hosted import, or a joined bundle.
3. **An explicit record of docs.rs-facing assumptions**: targets, features, `docsrs` cfg, `DOCS_RS`, rustdoc args, and limit-sensitive facts.
4. **A diffable artifact** for “works locally, fails on docs.rs” investigations.
5. **A small issue/report bundle** maintainers can hand to upstream docs.rs or coworkers.
6. **A drift-cause summary** that keeps hosted facts, local observations, and conservative inference separate.

# Persona / who it’s for

- crate maintainers who care about docs.rs reliability
- release engineers gating docs before publish
- docs-heavy library teams using `#[cfg(docsrs)]` or docs.rs metadata
- tooling authors integrating docs checks into CI
- maintainers filing upstream docs.rs or nightly-breakage issues

# Users & user stories

- **Maintainer**: “Tell me exactly what docs.rs-facing config we used, which targets became active, and whether we exceeded any known limits.”
- **Reviewer**: “Show me what changed in our docs.rs posture after this metadata or nightly bump.”
- **CI owner**: “Emit one artifact I can archive whenever the docs preflight fails.”
- **Upstream issue filer**: “Attach a compact bundle that captures the local attempt and how it differed from hosted docs.rs.”

# Prior art (and why it’s insufficient)

- docs.rs build and metadata pages document the hosted environment and knobs.
- the docs.rs team now publishes the current nightly toolchain and current sandbox limits on the builds page.
- the October 2025 docs.rs target-change announcement makes target drift a real maintenance concern.
- the docs.rs repository explains how to reproduce the hosted environment more faithfully.
- `cargo-docs-rs` already helps run `cargo rustdoc` with docs.rs-oriented options.

That is excellent substrate, but it is still mostly **execution guidance**, not a compact **receipt / diff / issue-bundle workflow**. The docs.rs build page itself says `cargo docs-rs` can catch many issues while not perfectly replicating the hosted environment. That is exactly where a parity-and-evidence crate becomes valuable.

# Design goals

1. **Parity-first** — optimize for explaining docs.rs-facing behavior, not replacing docs.rs.
2. **Environment-explicit** — toolchain, targets, metadata, cfg scope, and limit assumptions must always be visible.
3. **Diff-friendly** — metadata/nightly/target changes should be easy to compare.
4. **Issue-bundle-ready** — artifacts must be small enough to attach to CI and bug reports.
5. **Honest about fidelity** — distinguish hosted facts, local facts, and conservative inference.

# MVP surface

- Minimal types: `DocsRsProfile`, `DocsRsEnvReceipt`, `DocsRsConfigReport`, `DocsRsLimitReport`, `DocsRsResult`, `PreflightFidelityReport`, `HostedBuildImportReceipt`, `DriftCauseReport`, `DocsRsDiff`, `DocsRsBundle`
- Minimal functions:
  - `capture_docsrs_bundle()`
  - `normalize_docsrs_metadata()`
  - `collect_limit_report()`
  - `classify_fidelity()`
  - `import_hosted_build_receipt()`
  - `explain_drift_causes()`
  - `diff_docsrs_bundles()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `hosted-build-logs`
  - `markdown`
  - `redaction`

# Compatibility story

- Works above `cargo rustdoc` and can optionally wrap `cargo-docs-rs` when available.
- Must preserve the difference between “hosted docs.rs fact”, “local approximation”, and “best-effort inference”.
- Should stay useful even as docs.rs changes nightly toolchains, because the bundle records what was believed at run time.
- Can remain useful without full local docs.rs builder reproduction, because the artifact is about **explanation and handoff**, not perfect emulation.

# Conformance & fixtures

- One fixture with `#[cfg(docsrs)]`-dependent docs behavior where the dependency/workspace lane differs from the final rustdoc lane.
- One fixture with custom `[package.metadata.docs.rs]` targets and rustdoc args.
- One fixture where leaving target defaults implicit changes the published docs posture after the October 2025 target-list shift.
- One fixture that violates the documented max-target policy and emits a limit-risk report.
- One fixture that writes to a read-only source tree and should instead use `OUT_DIR`.
- One fixture that passes local preflight but still depends on network access that hosted docs.rs blocks.
- One fixture that depends on a native dependency absent from the docs.rs build environment.
- One fixture where the hosted build log is truncated and only a conservative manual-review summary is honest.
- Goldens for `metadata_changed`, `default_targets_shifted`, `limit_risk_detected`, `readonly_fs_violation_risk`, `network_policy_risk`, `missing_native_dependency`, `log_truncation`, `hosted_vs_local_drift`, and `manual_review_required`.

# Path to boring stability

- Stabilize the receipt/config/diff schema before adding rich dashboards.
- Start with local preflight capture and optional hosted-build import.
- Keep the first limit taxonomy small and tied to documented docs.rs constraints.
- Prefer explicit uncertainty over fake precision about hosted behavior.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that capture one docs.rs-oriented local build, record effective docs.rs metadata and target assumptions, classify evidence fidelity, summarize limit-sensitive facts, and emit a diffable issue/review bundle.

# De-risk plan

1. Start with metadata/receipt capture before trying to ingest hosted build logs.
2. Use documented docs.rs limits, cfg-scope rules, target rules, and hosted-build-summary surfaces as the initial truth source.
3. Keep drift-cause classification coarse until real issue bundles prove what is stable.
4. Validate on one docs-heavy crate using `#[cfg(docsrs)]`, one multi-target crate, one read-only-build fixture, and one missing-native-dependency fixture.

# Non-goals

- Not a replacement for docs.rs.
- Not a perfect local emulator of the full hosted environment.
- Not a generic docs renderer.
- Not a new nightly-management tool.

# Architecture & API sketch

```rust
pub struct DocsRsResult {
    pub success: bool,
    pub phase: String,
    pub notes: Vec<String>,
}

pub fn capture_docsrs_bundle(root: &Path) -> Result<DocsRsBundle>;
pub fn normalize_docsrs_metadata(root: &Path) -> Result<DocsRsConfigReport>;
pub fn collect_limit_report(bundle: &DocsRsBundle) -> DocsRsLimitReport;
pub fn diff_docsrs_bundles(old: &DocsRsBundle, new: &DocsRsBundle) -> DocsRsDiff;
```

Bundle draft: `docsrs-profile.toml`, `docsrs-env.receipt.json`, `docsrs-config.report.json`, `docsrs-limit.report.json`, `docsrs-results.json`, `preflight-fidelity.report.json`, `hosted-build-import.receipt.json`, `drift-cause.report.json`, `docsrs-diff.json`, `notes.md`.

# Security / safety model

- Treat build logs and imported hosted facts as untrusted input.
- Support redaction of local paths, usernames, and unpublished crate names.
- Never present a local approximation as equivalent to hosted docs.rs when the docs themselves say otherwise.
- Preserve whether a result depended on nightly-only, docs.rs-only, or cross-compiled-target assumptions.

# Maintenance & governance plan

- Track docs.rs build/metadata documentation, target-list changes, build-summary surfaces, and builder-environment changes.
- Keep schemas compact and versioned.
- Maintain fixtures for metadata drift, `docsrs` cfg behavior, read-only-path behavior, network policy, native dependency failures, and target-limit issues.
- Publish guidance for CI systems on stable versus best-effort fields.

# Milestones

## 0.1
- metadata capture
- environment receipt
- local preflight bundle
- fidelity classification

## 0.2
- diffing
- limit report
- optional hosted-build import
- drift-cause summaries

## 1.0
- stable bundle schema
- issue-template integrations
- curated docs.rs drift corpus

See also: `meta/docsrs-build-parity-product-plan-2026-03-17.md`.

# Open questions

- How much hosted-build data should be imported before the tool becomes too network- or site-shape-dependent?
- Which docs.rs environment facts belong in the core schema versus optional adapters?
- Should the crate learn how to fetch hosted build facts itself, or stay purely local-first and import-only?
- Should default-target drift be surfaced as a hard warning only when docs posture was implicit?

# Sources

- Docs.rs builds page: https://docs.rs/about/builds
- Docs.rs metadata page: https://docs.rs/about/metadata
- docs.rs target-change announcement: https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- docs.rs repository README: https://github.com/rust-lang/docs.rs
- `cargo-docs-rs`: https://crates.io/crates/cargo-docs-rs
