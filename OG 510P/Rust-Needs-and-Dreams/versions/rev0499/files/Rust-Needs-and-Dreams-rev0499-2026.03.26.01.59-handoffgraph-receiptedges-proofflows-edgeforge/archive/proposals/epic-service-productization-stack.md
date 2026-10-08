# Epic Proposal: Service Productization Stack (`cargo service product` + `service-product-pack/v0`)

## Why this is worthy
Rust already has credible service ingredients, but it still lacks a **portable product layer for boring production services**.

The ecosystem signal is unusually aligned:
- The 2024 State of Rust survey says Rust is especially popular for **server backends, web and networking services, and cloud technologies**, and 82% of respondents using Rust at work said it helped their company achieve its goals.
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- The 2025 survey says overall results closely match the prior year, keeps **resource usage** and **debugging** in the pain set, and says online documentation remains the preferred canonical reference.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust’s 2026 flagship themes still keep **Just Add Async** active, which is a reminder that lifecycle, shutdown, task ownership, and async ergonomics are still moving rather than settled.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `axum` already offers a strong request/response substrate and explicitly leans on `tower` + `tower-http` instead of inventing its own middleware universe.
  https://docs.rs/axum/latest/axum/
  https://docs.rs/tower/latest/tower/
  https://docs.rs/tower-http/latest/tower_http/
- Tokio’s own documentation treats **graceful shutdown** and **tracing** as first-class async-service topics, which is exactly the boundary where “works locally” often stops being enough.
  https://tokio.rs/tokio/topics/shutdown
  https://tokio.rs/tokio/topics/tracing
- `config` makes layered configuration a real reusable lane, `tracing-opentelemetry` makes trace export a real attachable lane, and `apalis` shows that background work already has enough substrate to deserve first-class contracts.
  https://docs.rs/config/latest/config/
  https://docs.rs/tracing-opentelemetry/latest/tracing_opentelemetry/
  https://docs.rs/apalis/latest/apalis/
- docs.rs target changes and the `doc_cfg` push make service support claims more dynamic and more reviewable than “it built once on CI”.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
  https://rust-lang.github.io/rust-project-goals/2025h2/rustdoc-doc-cfg.html

But the ecosystem still has no single honest handoff for **service-as-product truth**.

That means maintainers, operators, release reviewers, and tools still have to reconstruct the answer from:
- router code;
- framework docs and snippets;
- environment-variable lore;
- tracing setup fragments;
- background-worker crates and runbooks;
- support matrices and CI history;
- and ad hoc deployment or incident notes.

The missing contribution is a thin portable layer above those pieces, not a replacement for them.

## Proposal
Define a **Service Productization Stack** with:
- a reference aggregation CLI, `cargo service product`;
- a thin linked bundle, `service-product-pack/v0`;
- imported evidence from:
  - `service-pack/v0`
  - runtime-settings reports and checked config examples
  - observability profiles and validation reports
  - async-lifecycle / replay / shutdown reports
  - background-work catalogs and retry/idempotency reports
  - `support-pack/v0` and `doc-pack/v0`
  - optional release / policy / incident imports
- stable stack-level artifacts:
  - `service-product-brief/v0`
  - `service-runtime-brief/v0`
  - `service-work-brief/v0`
  - `service-support-brief/v0`
  - `service-product-diff/v0`

## Reference CLI shape
- `cargo service product export`
  - emit `service-product-brief/v0` from imported service-surface and runtime-settings evidence
- `cargo service product observe`
  - emit `service-runtime-brief/v0` from observability and async-lifecycle imports
- `cargo service product work`
  - emit `service-work-brief/v0` from background-work imports
- `cargo service product support`
  - emit `service-support-brief/v0` from support-envelope and docproof imports
- `cargo service product diff --against <ref|version|path>`
  - emit `service-product-diff/v0`
- `cargo service product pack`
  - produce `service-product-pack/v0`
- `cargo service product verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace `axum`, `tower-http`, Tokio, `config`, tracing, background-job runtimes, deployment platforms, or incident tools.

## What `service-product-pack/v0` should contain
- `manifest.json`
- `service-product-brief.json`
- `service-runtime-brief.json`
- `service-work-brief.json`
- `service-support-brief.json`
- optional `service-product-diff.json`
- imported `service-pack` pointer or embedded attachment
- imported runtime-settings, observability, async-lifecycle, background-work, and support/docs attachments
- checksums, provenance, and generator identity
- optional release / policy / incident consumer pointers

## Design principles
- **Route truth is not enough.** HTTP shape alone does not tell operators what the service actually promises.
- **Config truth is part of the product.** Defaults, precedence, aliases, reloadability, and secret posture cannot stay buried in examples.
- **Telemetry is evidence, not a substitute contract.** Logs/traces/metrics must connect back to declared service and work identities.
- **Background work is first-class.** Jobs, workflows, retries, and drain behavior must not stay implicit inside services.
- **Support/docs posture is imported, not guessed.** docs.rs, cfg markers, target defaults, and runtime floors must travel as explicit claims.
- **Consumers import bounded conclusions.** Release, policy, incident, support, and atlas consumers should each get explicit handoff boundaries.
- **No framework coronation.** A good service-product layer should help `axum`/`tower`, `actix-web`, `poem`, job workers, and adjacent runtimes without anointing one as the only serious choice.

## Early implementation order
1. HTTP surface + layered config lane
2. telemetry + runtime-correlation lane
3. graceful shutdown + background-work lane
4. support/docs/runtime-floor lane
5. release / policy / incident consumer lane

That order follows the real pressure gradient: first prove maintainers can publish boring service truth, then prove runtime evidence, then prove lifecycle/work semantics, then make support claims honest, and only then let downstream governance consumers rely on it.

## Non-goals
- a Rust Spring Boot equivalent;
- a universal service platform or hosted control plane;
- another framework bake-off;
- one mega-schema that flattens routes, config, telemetry, shutdown, jobs, and support into a fake maturity score;
- a promise that service-product packs alone prove operational excellence.

## Success bar
This becomes worthy when a maintainer, operator, release reviewer, or ecosystem guide can answer:
- what service boundary is official,
- which settings and defaults actually matter,
- what telemetry and runtime evidence should exist,
- what background work and shutdown semantics are promised,
- what support/docs/runtime-floor claims are attached,
- and what changed between versions or deployment profiles,

without scraping router code, env var docs, runbooks, and issue threads.

## Read this with
- `design/service-productization-stack.md`
- `design/service-productization-pilot-program.md`
- `design/service-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/observability-kit.md`
- `design/async-reliability-stack.md`
- `design/background-work-kit.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
