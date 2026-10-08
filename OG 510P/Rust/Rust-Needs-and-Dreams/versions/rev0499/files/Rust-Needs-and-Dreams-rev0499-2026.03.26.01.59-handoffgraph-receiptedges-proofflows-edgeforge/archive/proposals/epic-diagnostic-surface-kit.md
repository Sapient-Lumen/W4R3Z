# Epic proposal: Diagnostic Surface Kit

## Thesis
Rust already has serious building blocks for error handling and reporting.
The next high-leverage contribution is not another error wrapper.
It is a **shared diagnostic-surface layer** that turns codes, help/docs mappings, redaction rules, response renderings, and checked failure examples into durable engineering artifacts.

That would be a worthy ecosystem contribution because it helps:
- application authors treat failures as a supported interface rather than incidental `Display` strings,
- operators and support teams search/share stable diagnostics instead of reverse-engineering stack traces,
- services keep HTTP/JSON error bodies aligned with internal diagnostic identities,
- and docs/CI/release processes attach reviewable failure evidence alongside binaries, schemas, and command surfaces.

## Why now
The timing is good because Rust already has the ingredients, but still not the contract:
- `thiserror` and `anyhow` make typed/contextual errors routine,
- `miette` already defines rich diagnostic metadata,
- `error-stack` and `tracing-error` already show that attachments/backtraces/span traces are a real operational concern,
- `serde_path_to_error` already proves users care about precise failure locations,
- Problem Details crates already exist because service errors are a real user-facing API surface,
- and the official survey/debugging signals still say developers lose time on debugging and failure understanding.

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

## Proposed shape
Ship a narrowly scoped reference stack:
1. schemas for `diagnostic-catalog/v0`, `diagnostic-mapping-plan/v0`, `diagnostic-example-catalog/v0`, `diagnostic-check-report/v0`, and `diagnostic-pack/v0`
2. adapters for popular Rust error/diagnostic crates and HTTP error-surface crates
3. fixture validation for CLI stderr, JSON outputs, and HTTP Problem Details responses
4. docs/reference generation so troubleshooting pages and diagnostic catalogs can be derived and checked
5. release/CI examples showing diagnostic packs attached to binaries, services, command docs, and incident packs

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s crates legible together rather than trying to replace them.

## Initial pilots
- one CLI app using `thiserror`/`miette` with checked stderr examples and searchable codes
- one service using typed errors + Problem Details responses + JSON fixture checks
- one app using `error-stack` or `tracing-error` with explicit redaction/backtrace/span-trace policy
- one parser/config/schema-heavy tool using path-aware diagnostics from `serde_path_to_error`

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve diagnostic identity, severity, help/docs links, and exposure posture
2. **v0.2 adapters**
   - support `miette`, `error-stack`, `tracing-error`, common `thiserror`/`anyhow` patterns, and Problem Details crates
   - capture surface mappings and redaction/report policy honestly
3. **v0.3 cross-kit integration**
   - integrate with Command Surface, DocProof, Observability, Incident, Replay, and Runtime Settings workflows
   - support diff/baseline workflows across releases and deployment modes
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact error crate stack

## Success metrics
- Teams can review failure-surface changes as explicit interface artifacts rather than grep-driven string diffs.
- Stable diagnostic ids/help/docs remain aligned across CLI, HTTP, and machine-readable outputs.
- Redaction/backtrace/span-trace posture becomes visible in CI and release review.
- Troubleshooting docs and checked response fixtures stay aligned with the emitted diagnostics.
- Rust CLIs and services become easier to operate and support without forcing one error-handling crate on everybody.

## Archive fit
This proposal adds an underrepresented but important domain to the concise archive: **failure surfaces as a supported interface**.
It also fills a deliberate hole left by Command Surface Kit, DocProof Kit, Observability Kit, Debugger Experience Kit, and Incident/Replay proposals. Those proposals touch failures from adjacent angles, but none of them tries to become the portable contract for declared diagnostic identities, redaction policy, surface mappings, and checked renderings themselves.
Diagnostic Surface Kit is the missing substrate that can travel alongside docs, releases, services, and support workflows without being absorbed by any one of them.
