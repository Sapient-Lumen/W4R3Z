---
id: P-0533
title: Error Surface Contract Kit — stable error identity, audience modes, remediation receipts, and sensitivity posture
status: idea
domains: [dx, libraries, cli, diagnostics, operations, support]
last_reviewed: 2026-03-21
evidence:
  - https://doc.rust-lang.org/std/error/trait.Error.html
  - https://docs.rs/anyhow/latest/anyhow/
  - https://docs.rs/thiserror/latest/thiserror/
  - https://docs.rs/miette/latest/miette/
  - https://docs.rs/error-stack/latest/error_stack/
  - https://docs.rs/snafu/latest/snafu/
  - https://docs.rs/ariadne/latest/ariadne/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
---

# Problem

Rust has excellent **error-building blocks**, but it still lacks one boring crate that lets maintainers publish a **reviewable error contract** for downstream users.

Today’s substrate is real and useful:

- `std::error::Error` gives the ecosystem a shared baseline around `Display`, `Debug`, `source()`, and emerging typed context via `provide()`;
- `thiserror` makes public error types cheap to maintain without forcing the derive crate into the public API surface;
- `anyhow` makes application-level context layering ergonomic;
- `miette` and `ariadne` make rich diagnostic rendering practical;
- `error-stack` and `snafu` let teams accumulate context, attachments, reports, and backtraces.

But those pieces do **not** by themselves answer the support questions people actually hit in production, libraries, CLIs, services, and internal tooling:

- which error **codes or identities** are stable enough to automate against,
- which output is meant for **end users**, which is for **operators/developers**, and which is for **machine readers**,
- which errors carry an actual **next action** versus ornamental prose,
- whether backtraces, attachments, file paths, snippets, request IDs, or local context might leak sensitive information,
- and whether a crate’s “great error messages” claim survives JSON/API surfaces, logs, docs, and support bundles.

The missing crate is therefore **not** another error type, another derive macro, or another pretty renderer.
It is an **Error Surface Contract Kit**: one receiver-facing layer that can publish stable receipts for error identity, audience mode, remediation surface, and sensitivity posture.

# Main judgment

This is worthy because it solves a wide and recurring seam across Rust software:

- library authors who need stable public error promises without freezing internal implementation details,
- CLI/tool authors who want human-friendly diagnostics without accidentally breaking automation,
- service teams who need machine-readable codes while still keeping operators informed,
- platform/security teams who need to know whether logs and reports are safe to export,
- and support engineers who need one compact artifact instead of reading derive macros, renderers, and examples to infer the contract.

The missing value is not “nicer error strings”.
The missing value is **error-support posture with receipts**.

# What it provides

- `error-identity.receipt.json` — stable code/class/variant commitments, whether identity is public API, and what can change without breaking consumers.
- `audience-mode.receipt.json` — whether a given surface is for end users, operators, developers, or machine readers, and what detail level belongs there.
- `remediation-surface.report.json` — which errors have actionable hints, documented next steps, retry guidance, or deep-linkable docs, plus where the advice came from.
- `sensitivity-posture.receipt.json` — whether paths, snippets, secrets, tokens, user data, attachments, or backtraces may appear, and what redaction/waiver posture applies.
- `error-surface.summary.md` — a compact human summary for API docs, runbooks, and support bundles.
- `error-surface.diff.json` — compares two releases or two configured modes and classifies `identity_changed`, `audience_changed`, `remediation_changed`, and `sensitivity_changed`.
- `cargo error-surface inspect` — capture one crate/application error contract.
- `cargo error-surface gate` — fail review when a promised code, audience mode, or redaction posture drifted.
- `cargo error-surface bundle` — produce a small support artifact for docs/release review/onboarding.

# What the crate should provide other people

1. **Stable error identity** without forcing downstream readers to reverse-engineer enum variants or stringly-typed prose.
2. **Audience separation** so human terminal reports, machine JSON payloads, logs, and docs do not masquerade as the same contract.
3. **Actionability receipts** so “help text available” is not confused with “there is a reliable fix or retry path.”
4. **Sensitivity posture** so a polished report does not quietly become an unsafe report.
5. **Diffable support promises** across versions, profiles, and rendering modes.
6. **One boring export format** that fits release review, support docs, and internal platform policy.

# Personas / who it’s for

- library maintainers with public error APIs
- CLI and developer-tool authors
- service/backend teams emitting structured errors
- platform, SRE, and security teams
- framework authors who want downstream-friendly error posture

# Users & user stories

- **Library maintainer**: “I want stable error codes and remediation docs without promising my entire internal enum layout forever.”
- **CLI author**: “I want friendly terminal reports and a separate machine contract for scripts.”
- **Service owner**: “I want JSON/API clients to see durable error identity while operators get richer context.”
- **Security reviewer**: “I want to know whether backtraces, attachments, or snippets can leak sensitive data.”
- **Support engineer**: “I want one export that tells me which messages are user-safe, which are internal, and which advice is authoritative.”

# Prior art (and why it’s insufficient)

- `std::error::Error` is the common substrate, but it does not define stable public codes, audience modes, or redaction posture.
- `thiserror` makes error definitions maintainable, but it intentionally stays out of public API branding and does not publish contract receipts.
- `anyhow` makes contextual application errors ergonomic, but it is optimized for local propagation, not exported public error support contracts.
- `miette` and `ariadne` make reports richer, but rich rendering is not the same as a stable multi-surface contract.
- `error-stack` and `snafu` make layered reports/backtraces/help practical, but they do not freeze what is safe to show on which surface or what is stable for automation.
- Old “diagnostic crates” answer rendering and spans; they do not answer whether a given error family is safe to expose, automatable by code, or actionable by users.

What remains missing is the **identity + audience + remediation + sensitivity** layer above today’s building blocks.

# Design goals

1. **Contract-first, not renderer-first.** Start from what is being promised to receivers.
2. **Stable identity without overfreezing internals.** Public error codes/classes should stay separate from internal representation choices.
3. **Audience separation.** Human-terminal, docs, operator logs, and machine/API surfaces should be modeled distinctly.
4. **Actionability honesty.** Hints, retryability, workaround text, and docs links should not collapse into one vague “helpful” label.
5. **Sensitivity honesty.** Backtraces, attachments, spans, paths, and data excerpts must not be treated as uniformly safe.
6. **Import, don’t absorb.** This crate should import from existing error/diagnostic/reporting crates when possible rather than replacing them.
7. **Broad applicability.** The same contract should work for CLIs, libraries, services, daemons, editors, and domain-specific tools.
8. **Reviewable drift.** Changes in public error posture should be diffable in CI and release review.
9. **Manual-review over fake certainty.** If a surface cannot be classified conservatively, emit `manual_review_required`.

# MVP surface

- Minimal types:
  - `ErrorIdentityReceipt`
  - `AudienceModeReceipt`
  - `RemediationSurfaceReport`
  - `SensitivityPostureReceipt`
  - `ErrorSurfaceSummary`
  - `ErrorSurfaceDiff`
- Minimal functions:
  - `inspect_error_surface()`
  - `classify_audience_modes()`
  - `diff_error_surface()`
  - `bundle_error_surface()`
- Feature flags:
  - `serde`
  - `miette-adapter`
  - `anyhow-adapter`
  - `error-stack-adapter`
  - `snafu-adapter`
  - `cli`

# First-class review objects

## `error-identity.receipt`

Captures:
- public code or code-family
- stability class (`public_contract`, `best_effort`, `internal_only`, `manual_review_required`)
- mapping basis (`enum_variant`, `explicit_code`, `http_status_plus_code`, `opaque_report`, `manual_policy`)
- docs/reference route

## `audience-mode.receipt`

Captures:
- surface name (`terminal_human`, `json_api`, `operator_log`, `developer_debug`, etc.)
- intended audience
- detail posture
- whether source chains / backtraces / attachments are included
- compatibility/stability promise

## `remediation-surface.report`

Captures:
- whether a hint exists
- whether a next step is authoritative, speculative, or missing
- whether retry guidance exists and under what basis
- docs URL / code explanation route
- whether human help and machine retryability differ

## `sensitivity-posture.receipt`

Captures:
- whether paths, spans, source snippets, user data, tokens, or attachments may appear
- backtrace posture
- export posture (`user_safe`, `operator_only`, `debug_only`, `redaction_required`, `manual_review_required`)
- redaction basis / waiver notes

# Suggested commands

- `cargo error-surface inspect`
- `cargo error-surface explain <code>`
- `cargo error-surface gate`
- `cargo error-surface diff old.json new.json`
- `cargo error-surface bundle`

# Compatibility story

- Stable Rust first for core receipts and adapters.
- Must work with crates that only implement `std::error::Error` plus `Display`.
- Should enrich receipts when `thiserror`, `miette`, `error-stack`, or `snafu` metadata is present.
- Must not require a specific renderer or terminal UI.
- Should tolerate mixed surfaces where one crate uses human reports locally and machine codes over network boundaries.

# Conformance & fixtures

- one fixture where a public code is stable but app-level `anyhow` context is intentionally unstable
- one fixture where human report help text exists but retryability remains `manual_review_required`
- one fixture where machine JSON and terminal human reports must not share the same audience-mode receipt
- one fixture where backtrace/attachments require an operator-only or redaction-required sensitivity posture

# Path to boring stability

- Freeze receipt vocabulary before deep framework integrations.
- Start with read-only inspection and diffing rather than automatic error rewrites.
- Prefer explicit manual overrides over guessing public compatibility from arbitrary strings.
- Keep remediation and sensitivity posture conservative when sources disagree.
- Export tiny artifacts suitable for docs, CI, and support tickets.

# Non-goals

- Not a replacement for `thiserror`, `anyhow`, `miette`, `error-stack`, `snafu`, or `ariadne`.
- Not a universal runtime exception framework.
- Not a logging system.
- Not a promise that every crate must expose stable string messages.
- Not a policy engine for secrets in general outside the error/report lane.

# Architecture & API sketch

```rust
pub struct ErrorIdentityReceipt {
    pub subject: String,
    pub public_code: Option<String>,
    pub stability_class: StabilityClass,
    pub mapping_basis: MappingBasis,
    pub docs_route: Option<String>,
}

pub struct AudienceModeReceipt {
    pub surface_name: String,
    pub audience: Audience,
    pub detail_posture: DetailPosture,
    pub includes_source_chain: bool,
    pub includes_backtrace: bool,
}

pub fn inspect_error_surface(subject: &Path) -> Result<ErrorSurfaceBundle>;
pub fn diff_error_surface(old: &ErrorSurfaceBundle, new: &ErrorSurfaceBundle) -> ErrorSurfaceDiff;
```

# Maintenance & governance plan

- Keep receipt schemas compact and versioned.
- Publish fixture families for libraries, CLIs, and JSON/API surfaces.
- Keep adapters thin and observational rather than magical.
- Require every stable receipt family to have one “help exists but contract is still partial” fixture.
- Prefer conservative defaults with typed `manual_review_required` states.

# Adoption plan

1. Start as a standalone library plus cargo subcommand.
2. Prove value on CLI/library/service examples with mixed human and machine surfaces.
3. Add adapters for `thiserror`, `miette`, `error-stack`, and `snafu`.
4. Add CI/release-review recipes.
5. Only later consider framework-specific integrations.

# Open questions

- How much of error identity can be inferred safely versus declared manually?
- Should JSON/API error surfaces get their own stricter schema lane later?
- Which sensitivity facts belong here versus in broader redaction-policy crates?
- How should this crate treat localized messages versus stable codes?
- How much backtrace posture should be captured on stable Rust versus adapter-specific best effort?

# Sources

See front matter links.
