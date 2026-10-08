# Design: Diagnostic Surface Kit (`cargo diagnose`, `diagnostic-pack/v0`)

## Goal
Define a portable contract for declaring, validating, documenting, diffing, and reviewing Rust diagnostics: error codes, help/docs metadata, redaction policy, human renderings, HTTP/JSON mappings, and evidence that the declared failure surface still matches what the program emits.

This should **not** replace `thiserror`, `anyhow`, `miette`, `error-stack`, `tracing-error`, framework-specific response types, or Problem Details crates.
It should make them compose better and make failure interfaces reviewable.

## References (signals)
- `thiserror` is still the mainstream derive lane for typed `std::error::Error` values.
  https://docs.rs/thiserror
- `anyhow` is still the mainstream application-level context/backtrace lane.
  https://docs.rs/anyhow
- `miette` explicitly models rich diagnostics and `Diagnostic` metadata including code, severity, help, URL, labels, and source snippets.
  https://docs.rs/miette
  https://docs.rs/miette/latest/miette/trait.Diagnostic.html
- `error-stack::Report` already supports attachments, multiple backtraces, and span traces.
  https://docs.rs/error-stack/latest/error_stack/struct.Report.html
- `tracing-error` provides `SpanTrace`, which proves tracing context is part of real failure ergonomics.
  https://docs.rs/tracing-error
- `serde_path_to_error` demonstrates that data-path-aware failures matter enough to need reusable infrastructure.
  https://docs.rs/serde_path_to_error
- `problemdetails` and `problem_details` implement RFC 7807 / RFC 9457 Problem Details for HTTP APIs.
  https://docs.rs/problemdetails
  https://docs.rs/problem_details
- `axum` makes concrete error-to-response mapping a first-class application concern.
  https://docs.rs/axum/latest/axum/response/index.html
- The 2025 State of Rust survey still shows debugging/productivity pain as a major issue, and the Rust project launched a dedicated debugging survey in 2026.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

## Core components

### 1) `diagnostic-catalog/v0`
A design-time declaration of the diagnostics a binary/workspace/service claims to expose or consume.

Required ideas:
- subject identity (crate / workspace / binary / service / library API surface)
- diagnostic identity:
  - stable code or explicit `none`
  - title / short summary
  - severity and audience (`user`, `operator`, `developer`, `internal`)
  - stability posture (`official`, `best-effort`, `experimental`, `deprecated`, `internal-only`)
- metadata:
  - help text or help-template presence
  - docs / troubleshooting URL or internal reference
  - source-span support
  - backtrace / span-trace capability
  - field/path-location capability
- exposure policy:
  - allowed public surfaces (CLI, JSON, HTTP, logs, telemetry, docs)
  - redaction class (`public-safe`, `redacted`, `internal-only`, `environment-dependent`)
  - leak-risk notes for attachments/source excerpts
- compatibility notes:
  - renamed/replaced diagnostic ids
  - aliases
  - deprecation posture

Design rule: this catalog is about **declared failure identities**, not every private enum variant.

### 2) `diagnostic-mapping-plan/v0`
A machine-readable description of how declared diagnostics are rendered or translated across surfaces.

Likely fields:
- CLI/stderr rendering profile:
  - plain / graphical / narrated / color policy
  - exit-code mapping
  - source-snippet/label policy
- structured machine outputs:
  - JSON schema/profile id
  - included fields (code, message, help, docs URL, causes, path, correlation ids)
- HTTP service mapping:
  - Problem Details `type` / `status` / `title` strategy
  - extension-field policy
  - safe-detail/redaction policy
- logging / telemetry mapping:
  - required log fields
  - tracing/telemetry attribute names
  - correlation with trace/span/request ids
- unsupported/conditional lanes:
  - no-std / embedded / TTY-only / CI-only distinctions

Design rule: do not flatten all renderings into one fake canonical payload. Keep the mapping plan explicit.

### 3) `diagnostic-example-catalog/v0`
Inventory of reviewed diagnostic examples and attachments.

Possible entries:
- checked CLI stderr examples
- checked JSON failure fixtures
- checked HTTP Problem Details fixtures
- checked troubleshooting/doc examples
- illustrative-only examples
- source-snippet fixtures
- field/path failure fixtures

Each entry should record:
- diagnostic id(s)
- rendering surface
- checked vs illustrative status
- environment assumptions (TTY, locale, debug/release, redaction mode)
- input fixture pointer if applicable

### 4) `diagnostic-check-report/v0`
Evidence from validation runs.

Likely checks:
- duplicate/missing public codes
- diagnostics without help/docs metadata where policy requires it
- mapping drift across CLI/JSON/HTTP surfaces
- response-fixture mismatch
- redaction failures
- span/backtrace/path capability present or missing as expected
- examples/docs/fixtures stale or unverified
- deprecated/aliased diagnostics still intentionally supported or not

This is the review artifact CI and release workflows should diff.

### 5) `diagnostic-pack/v0`
Bundle format containing:
- `diagnostic-catalog/v0`
- `diagnostic-mapping-plan/v0`
- optional `diagnostic-example-catalog/v0`
- one or more `diagnostic-check-report/v0`
- optional attached response fixtures, rendered examples, source snippets, and raw framework/tool outputs

This is the unit that should travel through CI, release review, support docs, incident packs, and later archaeology.

### 6) `cargo diagnose`
Reference UX:
- `cargo diagnose init`
- `cargo diagnose catalog`
- `cargo diagnose check`
- `cargo diagnose diff`
- `cargo diagnose fixtures`
- `cargo diagnose pack`

`cargo diagnose` should begin as an explainer / adapter / packer.
It should not pretend to be the one true error-handling crate.

## Default policy
- **Separate declared diagnostic identities from surface mappings and from run evidence.**
- **Treat redaction/exposure policy as first-class metadata** instead of ad hoc formatter behavior.
- **Preserve raw response/rendering truth** for CLI examples, JSON fixtures, and problem-details bodies.
- **Distinguish checked examples from illustrative examples** so troubleshooting docs can stay honest.
- **Allow diagnostics to be intentionally internal-only** instead of forcing every error into a public code scheme.

## What the kit should provide to others
- **Command Surface Kit:** connect command failures to stable diagnostic ids and checked stderr examples.
- **DocProof Kit:** consume troubleshooting snippets and failure examples as checked learning surfaces.
- **Observability Kit:** attach diagnostic ids, severities, and safe metadata to logs/traces without owning the telemetry pipeline.
- **Incident Kit / Replay Kit:** package known diagnostics and rendered fixtures alongside failure reproductions.
- **Runtime Settings Kit / Database Contract Kit / Schema Contract Kit:** expose settings/query/schema validation failures as declared, reviewable diagnostics instead of raw strings.
- **Debugger Experience Kit:** keep debugger metadata separate while giving debugger/repro packs stable diagnostic ids to point at.

## Overlap boundaries
- **Not `thiserror` / `anyhow` / `snafu` / `error-stack` / `miette`:** those define or render errors; this kit packages the supported failure interface and evidence across them.
- **Not Observability Kit:** logs/traces/metrics/exporters remain a separate telemetry concern; this kit only supplies diagnostic identity and surface-mapping metadata that observability workflows may ingest.
- **Not Command Surface Kit:** command syntax/help/completions remain distinct from the failure surfaces the command emits.
- **Not Schema Contract Kit:** this is about failure interfaces, not success payload schemas, though HTTP problem-details mappings may attach schema references.
- **Not Incident or Replay:** those kits own response processes and reproductions; Diagnostic Surface Kit owns the declared diagnostic catalog and checked renderings.
- **Not a vendor/hosted error portal:** the value is the artifact and review workflow, not a centralized SaaS dashboard.

## Hard problems (explicitly scoped)
1. **Internal failures and public diagnostics are not identical**
   - many private error variants collapse into one public/operator-facing diagnostic.
   - v0 should model that intentionally.

2. **Surface mappings are heterogeneous**
   - TTY CLI output, JSON payloads, logs, and HTTP problem-details responses should not be flattened into one fake universal format.

3. **Redaction is contextual**
   - source excerpts, config values, query fragments, and attachments may be safe locally but unsafe in API responses or telemetry.

4. **Backtraces and span traces are capability-dependent**
   - reports must model whether they were requested, captured, redacted, or unavailable.

5. **Do not become a giant error framework**
   - the goal is portable contracts and validation, not replacing every existing error crate.

## Minimal adoption path
1. Publish schemas for `diagnostic-catalog/v0` and `diagnostic-check-report/v0`.
2. Add adapters for `miette`, `error-stack`, `tracing-error`, common `thiserror`/`anyhow` patterns, and HTTP Problem Details crates.
3. Support fixture validation for CLI stderr, JSON payloads, and HTTP responses.
4. Add docs/example generation so troubleshooting references and error catalogs can be checked.
5. Add diff/baseline support so release review sees failure-surface changes explicitly.

## Why this is an ecosystem contribution, not just repo hygiene
Rust already has enough error-handling machinery that the missing piece is no longer “yet another error crate.”
The missing piece is a portable diagnostic-surface contract that can travel through docs, CI, service interfaces, support playbooks, and incident archaeology.
That is a substrate contribution, not a convenience wrapper.
