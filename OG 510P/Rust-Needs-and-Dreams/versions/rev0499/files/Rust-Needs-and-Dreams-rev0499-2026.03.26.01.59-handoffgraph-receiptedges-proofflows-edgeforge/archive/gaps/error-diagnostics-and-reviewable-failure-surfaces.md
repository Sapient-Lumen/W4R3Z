# Gap: error diagnostics and reviewable failure surfaces

## What is missing
Rust has many good ways to **create**, **wrap**, and **print** errors, but it still lacks a **shared diagnostic-surface contract**.

Today there is no standard way to describe, exchange, and diff:
- which diagnostic codes and failure categories a binary/service actually exposes,
- which failures are stable public/operator-facing versus purely internal,
- which human help text, docs URLs, labels, and source snippets belong to each diagnostic,
- how a diagnostic maps across CLI, logs, JSON, and HTTP problem-details surfaces,
- what redaction policy applies to attachments, backtraces, span traces, and source excerpts,
- which examples and docs were actually checked,
- and what evidence exists that runtime error renderings still match the declared public failure interface.

That missing layer matters because Rust now has strong point tools for error derivation, context, pretty printing, tracing-aware attachments, and HTTP error bodies, but deployable applications still ship failure truth as a mixture of enum variants, ad hoc `Display` impls, `miette` annotations, framework-specific response mappers, and maintainer memory.

Sources:
- https://docs.rs/thiserror
- https://docs.rs/anyhow
- https://docs.rs/miette/latest/miette/trait.Diagnostic.html
- https://docs.rs/miette
- https://docs.rs/error-stack/latest/error_stack/struct.Report.html
- https://docs.rs/tracing-error
- https://docs.rs/serde_path_to_error
- https://docs.rs/problemdetails
- https://docs.rs/problem_details
- https://docs.rs/axum/latest/axum/response/index.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

## The current seam is awkward
The ecosystem clearly has ingredients:
- `thiserror` makes typed `std::error::Error` definitions routine,
- `anyhow` makes context + backtrace-friendly application errors routine,
- `miette::Diagnostic` already models codes, severity, help, URLs, source code, and labels,
- `error-stack` already models rich attachments, backtraces, and `SpanTrace` integration,
- `tracing-error` already captures tracing span context for failures,
- `serde_path_to_error` already shows that field/path-specific failure locations are operationally valuable,
- HTTP Problem Details crates already exist because service error responses are a real contract surface,
- and frameworks like `axum` already force applications to decide how concrete errors become responses.

But each real project still hand-assembles its failure story out of:
- error enums and wrapper types,
- `Display` strings,
- ad hoc error codes,
- docs links or issue references,
- CLI stderr formatting choices,
- JSON response bodies,
- framework-specific `IntoResponse` impls,
- tracing/log fields,
- redaction decisions,
- and whatever backtrace/span-trace story happened to be wired in.

The result is not that Rust lacks error crates.
The result is that there is no portable way to say:
- “these are the diagnostics we support users/operators seeing,”
- “these are their codes/help/docs mappings,”
- “these are the response/log/rendering surfaces they appear on,”
- “these attachments are safe to expose and these are internal-only,”
- or “these examples and HTTP/CLI renderings were actually checked in CI.”

This matters more now because the official 2025 State of Rust survey still lists debugging/productivity pain among the major problems people hit, and the Rust project launched a dedicated 2026 debugging survey to understand that gap better. Failure surfaces are not the whole debugging story, but they are one of the most user-visible parts of it.

Sources:
- https://docs.rs/thiserror
- https://docs.rs/anyhow
- https://docs.rs/miette/latest/miette/trait.Diagnostic.html
- https://docs.rs/error-stack/latest/error_stack/struct.Report.html
- https://docs.rs/tracing-error
- https://docs.rs/serde_path_to_error
- https://docs.rs/problemdetails
- https://docs.rs/problem_details
- https://docs.rs/axum/latest/axum/response/index.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

## Why this matters
This gap is bigger than “prettier error messages.”
It affects:
1. **operator trust** — error codes, help text, and docs links are part of the supported interface for CLIs and services;
2. **support cost** — stable, searchable diagnostics reduce issue-triage and migration confusion;
3. **security/privacy** — backtraces, attachments, query values, config snippets, and source excerpts need explicit exposure/redaction policy;
4. **service correctness** — HTTP error bodies and JSON failures should not drift independently from internal diagnostic identities;
5. **documentation quality** — examples, troubleshooting docs, and problem-details docs drift unless they share one declared diagnostic catalog;
6. **cross-tool composition** — Command Surface, DocProof, Observability, Incident, Replay, and Debugger tooling all benefit from durable diagnostic identities rather than raw strings.

Rust is increasingly used for CLIs, services, control planes, data tools, and infrastructure software. All of those need a coherent answer to “what failures do we intentionally expose, how do we identify them, and what evidence says the rendered surfaces still match?”

Sources:
- https://docs.rs/miette/latest/miette/trait.Diagnostic.html
- https://docs.rs/error-stack/latest/error_stack/struct.Report.html
- https://docs.rs/problemdetails
- https://docs.rs/problem_details
- https://docs.rs/axum/latest/axum/response/index.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## What “good” looks like
A worthy contribution here is **not** another error type, another derive macro, or another pretty-printer.

It is a shared diagnostic-surface boundary:
- one `diagnostic-catalog/v0` describing public/internal diagnostic identities, codes, severities, docs/help metadata, and exposure/redaction posture,
- one `diagnostic-mapping-plan/v0` describing how diagnostics map to CLI stderr, structured JSON, HTTP Problem Details, logs, and telemetry fields,
- one `diagnostic-example-catalog/v0` inventorying checked and illustrative failure examples, snippets, troubleshooting docs, and response fixtures,
- one `diagnostic-check-report/v0` recording uniqueness, missing docs/help, surface drift, redaction violations, response-shape mismatches, and example/doc freshness,
- and one `diagnostic-pack/v0` bundle for CI, release review, support docs, incident packs, and archaeology.

That would let Rust projects expose a reviewable failure interface the same way command surfaces, schema surfaces, runtime-settings surfaces, and release surfaces increasingly deserve reviewable artifacts.
