# Buildscript UX Kit — support-bundle product plan (2026-03-23)

This note turns **P-0046 Buildscript UX Kit** into a tighter product plan.

## Product thesis

The crate should not try to explain all of Cargo.
It should provide one boring support bundle that makes `build.rs` failures and suspicious behavior easier to review.

The core user question is:

> “This build-script run went wrong. What happened, what mattered, and what should I try next?”

## Who it serves

### Primary users
- developers blocked on install or first build,
- maintainers triaging recurring `build.rs` issues,
- CI owners who want machine-readable gates instead of raw-log archaeology,
- IDE/editor wrappers that want structured summaries.

### Secondary users
- buildscript-test authors,
- native-deps and FFI tooling,
- docs.rs parity tooling that needs a stable representation of build-script behavior.

## What it should provide other people

A good `0.1` should export:

### `buildscript-report.json`
Structured report with:
- observed directives,
- emitted warnings/errors,
- exit status,
- normalized paths/placeholders,
- redaction state,
- relevant environment observations,
- manual-review markers.

### `buildscript-summary.txt`
A short human summary answering:
- which crate/build script failed,
- which warning or missing tool mattered most,
- what next actions are most plausible.

### `policy-gate.report.json`
A CI-facing result that says whether current workspace policy passed, for example:
- warnings from build dependencies,
- unexpected env reads,
- missing `rerun-if-*` discipline,
- missing redaction allowlist,
- forbidden network/tool invocation classes when a policy is enabled.

### `support-snapshot.redacted.txt`
Optional minimized text bundle that can be attached to issues without the entire raw log.

## Real `0.1` command surface

- `cargo buildscript report -- <cargo args...>`
- `cargo buildscript summarize path/to/buildscript-report.json`
- `cargo buildscript gate --policy path/to/policy.toml -- <cargo args...>`
- `cargo buildscript redact path/to/buildscript-report.json`

## Recommended crate split

- `buildscript-report-core`
  - typed report model,
  - directive normalization,
  - redaction model,
  - summary renderer.
- `cargo-buildscript-report`
  - CLI / cargo-subcommand UX,
  - process execution and capture.
- optional later `buildscript-policy`
  - reusable policy evaluation module.

## Theory of operation

### Inputs
- captured stdout/stderr from build scripts,
- Cargo invocation metadata,
- selected environment variables,
- optional workspace policy config.

### Processing
- parse Cargo build-script directives,
- normalize paths and temp locations,
- classify likely root causes,
- map observations into a small stable schema,
- produce both machine and human outputs.

### Outputs
- typed report,
- human summary,
- gate result,
- optional redacted support bundle.

## Feature planning

### Phase 0.1
- normalized directive capture,
- summary rendering,
- redaction placeholders,
- workspace policy gates,
- stable JSON schema.

### Phase 0.2
- diff mode between two reports,
- known-probe heuristics (`pkg-config`, `vcpkg`, `bindgen`, CMake, etc.),
- docs.rs-oriented mode highlighting read-only/network/resource issues.

### Phase 0.3
- richer integration with P-0059 fixture corpora,
- imported reports from CI artifacts,
- ecosystem adapters for editors and bots.

## Refusal boundaries

The crate must not pretend to answer:
- full Cargo rebuild causality,
- whether a native dependency is correct on every platform,
- or whether a single observed run proves long-term support.

It should be willing to say:
- “manual review required,”
- “policy failed but root cause is ambiguous,”
- or “the bundle is incomplete because raw execution context was unavailable.”

## Why this crate is timely

Cargo still documents conservative build-script rerun behavior when `rerun-if-*` is absent, and Cargo still needs a FAQ entry for unexpected rebuilds. At the same time, Cargo’s build-dir changes and docs.rs’ explicit sandbox conditions mean more teams need supportable explanations, not raw folklore.

## Good first proving grounds

- a `pkg-config`-missing failure,
- a build script that reruns too broadly because it omitted `rerun-if-*`,
- a docs.rs-only failure caused by read-only or network assumptions,
- a build script that infers target-dir from `OUT_DIR` and breaks under layout changes.

## Sources

- Cargo build scripts reference — https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo FAQ (“Why is Cargo rebuilding my code?”) — https://doc.rust-lang.org/cargo/faq.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo release notes (`OUT_DIR` build-time behavior change) — https://doc.rust-lang.org/beta/releases.html
- docs.rs builds — https://docs.rs/about/builds
