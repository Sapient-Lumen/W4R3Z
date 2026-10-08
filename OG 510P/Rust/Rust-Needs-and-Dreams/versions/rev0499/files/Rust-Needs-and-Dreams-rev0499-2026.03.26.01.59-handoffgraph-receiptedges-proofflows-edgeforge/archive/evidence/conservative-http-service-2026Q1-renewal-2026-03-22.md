# Renewal receipt: conservative HTTP/service baseline (2026-03-22)

## Subject
- default card: `defaults/conservative-http-service-2026Q1.md`
- review date: 2026-03-22
- archive revision: rev0380
- scope: conservative HTTP/service baseline for stable Rust, ordinary server teams, Tokio-shaped async posture
- non-goal: package-admission or security signoff for a public internet service

## Renewal verdict
**keep with caveats**

The lane still reads correctly as:
- `tokio` runtime,
- `axum` as the default framework,
- `tower-http` as the middleware vocabulary,
- `tracing` / `tracing-subscriber` for diagnostics,
- `serde` for payload/config structure,
with **Actix Web** kept visible as a serious alternative.

The caveat is the same one that made the lane hard in the first place:
this is a **coherent default for an app-shaped service**, not a universal answer for runtime-neutral async design, safety-tilted services, or every public-facing production threat model.

## Canon import checked this round
Primary documentation surfaces re-read:
- Tokio runtime and task docs:
  https://docs.rs/tokio/latest/tokio/runtime/struct.Runtime.html
  https://docs.rs/tokio/latest/tokio/task/fn.spawn.html
- axum overview and extractors:
  https://docs.rs/axum/latest/axum/
  https://docs.rs/axum/latest/axum/extract/
- tower-http tracing and CORS:
  https://docs.rs/tower-http/latest/tower_http/trace/
  https://docs.rs/tower-http/latest/tower_http/cors/
- tracing-subscriber:
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/fmt/
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/filter/struct.EnvFilter.html
- Serde:
  https://serde.rs/
- Actix Web guides and docs:
  https://actix.rs/docs/
  https://docs.rs/actix-web/latest/actix_web/

Canon judgment:
- the Tokio + axum + tower-http lane is still unusually coherent and well-documented for ordinary service work;
- Actix still deserves explicit visibility as a serious alternative rather than being erased by default-card convenience.

## Registry / supply-chain import
Public ecosystem signals checked:
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RustSec advisories:
  https://rustsec.org/advisories/

What this receipt takes from those sources:
- service defaults should now assume Security-tab review and exact crate identity are part of renewal discipline;
- recent advisories in service-adjacent crates (for example `quinn-proto`, `pingora-core`, and `pingora-cache`) reinforce that broad ecosystem maturity does **not** remove the need for per-project admission and threat review;
- recent malicious removals also reinforce the need to keep exact identifiers visible.

Exact identity notes for this lane:
- `tokio`, `axum`, `tower-http`, `serde`, `tracing-subscriber`, and `actix-web` should be recorded by exact name.
- This receipt is **not** making claims about a wider bucket called “Rust web crates”.

Registry judgment:
- the lane remains publishable as a public default card;
- but service teams should treat the receipt as a lane-level starting point, not as a substitute for package-admission review, advisory review, or deployment-specific threat work.

## API / compatibility import
Relevant current signals:
- `cargo-semver-checks` goal:
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- docs.rs changed default targets:
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- Cargo unstable/reference surface:
  https://doc.rust-lang.org/cargo/reference/unstable.html

Judgment:
- nothing here changes the lane-level answer yet;
- but support-envelope honesty matters more here than in the CLI lane because framework docs, runtime assumptions, and target expectations can drift independently;
- future renewals should keep docs-host target assumptions and runtime lock-in explicit.

## Maintenance / support-envelope import
Envelope facts that still hold:
- Tokio lock-in is a real tradeoff, not an incidental implementation detail.
- This lane is strongest when the team wants an application-shaped, runtime-coherent service stack.
- It is weaker when the project is library-first, runtime-neutral, safety-critical, protocol-heavy, or strongly shaped by local platform overlays.

Imported safety-critical signal:
- Rust’s safety-critical writeup explicitly recommends target-focused readiness checklists, dependency lifecycle patterns, safety-case-friendly async expectations, and C/C++ interop as part of the safety story.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

Maintenance judgment:
- the lane should stay public, but it should not be widened into a “secure/public-service default” without stronger evidence imports.

## Freshness / replay notes
Fresh inputs checked on 2026-03-22:
- Rust challenges post:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RustSec advisories:
  https://rustsec.org/advisories/
- docs.rs target-change post:
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/

Replay notes:
- future renewal should explicitly re-check service-framework advisories, runtime expectations, and support-envelope claims;
- if build-analysis or later Cargo report surfaces become useful for service-lane receipts, add them as attachments rather than letting the lane drift into anecdote.

## Lane judgment
Keep the lane, but keep the caveats loud.

Why:
- Rust still looks strong for CLI tools and web backends;
- the best public contribution here is still a bounded default, not a universal stack blessing;
- and the service lane especially needs visible escalation triggers for public-security, runtime-neutral, or safety-tilted work.

## Open watch items
- whether a separate **public safety-tilted service** card ever becomes justifiable;
- whether Actix should remain only a serious alternative or earn a sibling default card for a narrower project class;
- whether the lane should eventually split framework choice from middleware/diagnostics choice more explicitly.
