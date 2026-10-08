# Default card: Conservative HTTP/service baseline (2026 Q1)

Latest renewal receipt: `evidence/conservative-http-service-2026Q1-renewal-2026-03-22.md`


## Scope
This card applies to:
- ordinary internal or B2B HTTP APIs,
- service backends where async networking is expected,
- greenfield Rust services that want the current most legible conservative lane,
- and teams that prioritize **coherence + operability** over exotic runtime experimentation.

Assumptions:
- stable Rust;
- async runtime is acceptable;
- service is not constrained by `no_std` or embedded conditions;
- observability and middleware are real needs;
- the team wants a lane that fits ordinary Cargo/editor/debug workflows.

This is **not** the default for:
- runtime-neutral library design;
- actor-heavy or sync-handler-first preferences;
- specialized edge/network stacks with different protocol or performance constraints;
- or heavily regulated systems where more evidence imports are mandatory.

## Why this default now
Rust’s March 20, 2026 challenges post names async complexity and runtime lock-in as real ecosystem pain, but it also acknowledges that CLI and web backends are among Rust’s stronger lanes.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

For this exact project class, the archive’s current default is:
**Tokio runtime + axum router/extractor surface + tower/tower-http middleware + tracing-based diagnostics + serde-shaped request/response types.**

Why this wins here:
- Tokio’s runtime explicitly bundles the I/O driver, task scheduler, timer, and blocking pool that an ordinary async service expects.
  https://docs.rs/tokio/latest/tokio/runtime/struct.Runtime.html
  https://docs.rs/tokio/latest/tokio/task/fn.spawn.html
- axum’s official positioning is ergonomics + modularity, with macro-free routing, extractors, and direct use of the tower / tower-http ecosystem.
  https://docs.rs/axum/latest/axum/
  https://docs.rs/axum/latest/axum/extract/
- tower-http provides common middleware surfaces like tracing and CORS in the same service-oriented vocabulary.
  https://docs.rs/tower-http/latest/tower_http/trace/
  https://docs.rs/tower-http/latest/tower_http/cors/
- `tracing-subscriber` and Serde make diagnostics and typed request/response/config work in the same mainstream way many Rust services already expect.
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/fmt/
  https://serde.rs/
- Actix Web remains a serious alternative with strong docs and a pragmatic app model, which is exactly why the default must preserve alternatives rather than pretending axum is the only credible lane.
  https://actix.rs/docs/
  https://actix.rs/docs/application/
  https://docs.rs/actix-web/latest/actix_web/

## Default lane summary
### Default lane
- runtime: **Tokio**
- HTTP framework: **axum**
- middleware vocabulary: **tower + tower-http**
- typed request/response/config model: **Serde**
- diagnostics/logging: **tracing + tracing-subscriber**

### Serious alternative
- **Actix Web** when its app model, sync-handler ergonomics, or team familiarity make it the better project-specific fit.

### Watch / not-default here
- runtime-neutral abstractions for service libraries;
- more opinionated integrated frameworks;
- bespoke protocol stacks where HTTP-service framing is already the wrong abstraction.

## Slot guidance
### Runtime slot
Accept Tokio lock-in for this scope.
The archive should be honest that this is a coherence tradeoff, not a universal portability answer.

### Routing / handler slot
Prefer axum when the project values modularity, extractors, and tower-friendly composition.
Its fit with tower-http is a major reason it wins this default.

### Middleware slot
Prefer tower/tower-http vocabulary for common middleware such as tracing and CORS.
That keeps the lane composable and legible.

### Diagnostics slot
Default to tracing-based diagnostics from the start.
Service defaults that do not carry structured diagnostics usually create support debt quickly.

### Data slot
Prefer Serde-shaped types for payloads and config unless there is a compelling domain-specific reason not to.

## Serious alternatives and when they win
### Actix Web wins when
- the team prefers its application model and docs;
- its extractor/model better matches the codebase;
- or the project already has stronger local expertise there.

### Escalate away from this default when
- runtime neutrality is a primary requirement;
- library-first async interoperability matters more than app coherence;
- the service is mostly a polyglot host/boundary problem rather than an HTTP app problem;
- or safety/regulatory evidence requirements dominate framework ergonomics.

## Escalate to a project-specific brief when
- the service must stay deliberately runtime-agnostic;
- the team is already deeply committed to a different framework family;
- the deployment or observability environment imposes strong local overlays;
- a large existing workspace already dictates a different settings/middleware/testing posture;
- or the system is protocol-heavy enough that “HTTP service baseline” is no longer the right project class.

## Canonical references
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
  https://actix.rs/docs/application/
  https://docs.rs/actix-web/latest/actix_web/

## Renewal inputs
Recheck before renewal:
- async ecosystem motion, especially around runtime fragmentation and std-adjacent async work;
- axum / tower / Tokio canonical docs and obvious compatibility drift;
- Actix’s continuing fit as a serious alternative;
- crates.io / docs.rs review signals and any major docs-host support-envelope changes.

Signal refs:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

## Non-goals
- declaring Tokio+axum the universal Rust backend answer;
- solving runtime-neutral async library design;
- flattening framework choice into one permanent blessing;
- replacing service-productization, observability, package-admission, or local-overlay review.
