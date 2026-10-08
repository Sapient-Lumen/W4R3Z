# Design note: Service Productization Stack (Service Surface + Runtime Settings + Observability + Async Reliability + Background Work + Support Envelope)

## Goal
Define the **division of labor and consumer flow** between Rust service contracts, runtime configuration, telemetry, async/shutdown reliability, background jobs, and support claims so the ecosystem can make **boring production services** reviewable without anointing one framework, one app template, or one platform runtime as the default answer.

This is **not** a new top-level kit.
It is a stack note explaining how existing archive pieces should compose:
- [`design/service-surface-kit.md`](./service-surface-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/observability-kit.md`](./observability-kit.md)
- [`design/async-reliability-stack.md`](./async-reliability-stack.md)
- [`design/background-work-kit.md`](./background-work-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/policy-kit.md`](./policy-kit.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)

## Why this note is needed now
Rust’s current signals are no longer saying only “services are possible.” They are saying Rust is already a serious service language, but the ecosystem still lacks a **portable productization layer**:
- the 2024 State of Rust survey says Rust is especially popular for **server backends, web and networking services, and cloud technologies**;
- the same survey says companies are using Rust at work more, and that Rust helped many organizations achieve their goals;
- the 2024 and 2025 surveys both keep **debugging, resource usage, and async/tooling friction** in the problem set, which is exactly where production services suffer;
- the 2026 flagship themes keep **Just Add Async** active, which means service/runtime ergonomics are still moving rather than settled;
- the `doc_cfg` goal and docs.rs target changes show that **availability/support truth** is becoming more important to documentation and support claims, not less;
- Cargo keeps adding more machine-facing reporting and discovery work, which makes cross-tool service evidence more plausible than it used to be.

Together these signals justify treating service productization as a **frontier-worthy ecosystem seam** rather than leaving Rust services as a pile of framework docs, config crates, telemetry snippets, shutdown folklore, and operator runbooks.

## Stack layers

### 1) Service Surface: the request/response boundary
Service Surface owns the **public interaction contract** for a service:
- route identities
- methods/path/media-type posture
- middleware behavior
- checked exchanges
- service diffs and support classes

Service Surface answers questions like:
- “What does this service claim to do?”
- “Which routes are official versus internal?”
- “What middleware behavior is part of the contract?”
- “What changed between releases?”

Design rule: **service shape must not be inferred only from OpenAPI output, router code, or contract tests alone**.

### 2) Runtime Settings: the operational control plane
Runtime Settings owns the **configuration boundary**:
- setting identities and defaults
- source precedence
- secret and file-secret posture
- alias/rename/migration truth
- checked configuration examples
- validation and drift reports

Runtime Settings answers questions like:
- “Which knobs exist, which are stable, and where can they come from?”
- “Which values are reloadable or startup-only?”
- “Which config examples are promises instead of prose?”

Design rule: **runtime configuration must not hide inside README examples, environment-variable conventions, or one framework-specific loader**.

### 3) Observability: runtime evidence, not folklore
Observability owns the **telemetry and runtime correlation contract**:
- logs / traces / metrics / runtime-diagnostic posture
- semantic-convention subsets
- exporter and redaction policy
- validation vectors
- explainable runtime reports

Observability answers questions like:
- “What should this service emit in dev, CI, and prod?”
- “How do logs/traces/metrics correlate?”
- “What telemetry profile is actually supported?”

Design rule: **telemetry must not silently become the only source of truth about the service contract or its support story**.

### 4) Async Reliability: lifecycle and replay truth
Async Reliability owns the **task/runtime lifecycle boundary**:
- shutdown semantics
- cancellation posture
- runtime capability assumptions
- replay and deterministic-simulation handoff
- exact versus best-effort failure reproduction

Async Reliability answers questions like:
- “How does this service stop safely?”
- “What lifecycle evidence exists when it hangs or leaks work?”
- “When do we escalate from logs to replay or simulation?”

Design rule: **service operability must not pretend HTTP success means background task, stream, or shutdown correctness**.

### 5) Background Work: out-of-band execution truth
Background Work owns the **job/workflow side** of a service system:
- job and workflow identities
- trigger maps
- backend/execution posture
- retry/idempotency semantics
- durable workflow versioning and checks

Background Work answers questions like:
- “Which work is request-bound and which is out-of-band?”
- “What jobs are official?”
- “What happens on retries, delays, and version upgrades?”

Design rule: **background jobs must not be flattened into ordinary route behavior or hidden behind one queue crate’s API**.

### 6) Support Envelope + DocProof: support truth and docs truth
Support Envelope and DocProof together own the **supportability boundary**:
- runtime floors and target assumptions
- source-build versus released-binary posture
- docs surface truth
- platform/cfg availability claims
- checked examples and transcript evidence

This layer answers questions like:
- “Which operating systems, architectures, libc or SDK assumptions are official?”
- “Do the docs match the actual supported settings/routes/features?”
- “What does docs.rs or rustdoc show, and what target/cfg caveats remain?”

Design rule: **support claims must not be inferred from docs.rs defaults, one CI matrix, or one successful local run**.

### 7) Downstream consumers
The stack becomes worthy when real consumers can import it without flattening it:
- **Policy** can gate deployment or release on explicit evidence rather than shell-script folklore.
- **Release Pipeline** can attach service-surface/settings/observability/support artifacts to a release.
- **Incident / Replay** consumers can escalate from declared service evidence instead of starting from raw logs.
- **Atlas / learning** consumers can point users toward credible service stacks without inventing one mega-framework recommendation.

Design rule: **consumers import selected evidence; they do not redefine the service truth models**.

## What an epic contribution should look like in practice
A worthy contribution here is not “build the Rust Spring Boot.”
It is a portable, reviewable stack with clear boundaries:

1. **Route + settings first**
   - prove `service-surface` + `settings-schema` + checked examples on one real service;
2. **Telemetry second**
   - add `obs-profile`, `obs-report`, and validation vectors that correlate with the declared surface;
3. **Shutdown + work third**
   - attach async lifecycle evidence and out-of-band work catalogs without flattening them into HTTP behavior;
4. **Support/docs fourth**
   - prove docs.rs / `doc_cfg` / target / runtime-floor truth and checked docs/examples;
5. **Consumers fifth**
   - show one policy/release/incident/support consumer can import the stack honestly.

An eventual aggregate artifact may exist, but it should be a **thin pack of referenced artifacts**, not a new truth engine that erases the lane boundaries.

## Candidate artifact family
A worthy service-productization contribution should stay thin and linked instead of becoming a service mega-schema.
A plausible family is:
- `service-product-brief/v0`
- `service-runtime-brief/v0`
- `service-work-brief/v0`
- `service-support-brief/v0`
- `service-product-diff/v0`
- `service-product-pack/v0`

These artifacts should mostly reference lower-layer packs and checked attachments instead of replacing them.

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

This should remain a **composition layer**, not a framework, control plane, or deployment platform.

## Ranked first execution lanes
1. **HTTP service + config lane**
   - best first exporter because many Rust teams already have `axum`/`tower` + env/file configuration and need reviewable contracts more than more framework magic.
2. **Telemetry and runtime-correlation lane**
   - proves the stack can describe what should be emitted and how to validate it.
3. **Graceful shutdown + background-work lane**
   - makes operability real by modeling tasks, jobs, and workflows instead of only request handlers.
4. **Support/docs lane**
   - proves cfg/target/runtime-floor/docs truth instead of README optimism.
5. **Release/policy/incident consumer lane**
   - shows the stack matters beyond local engineering taste.

## Non-goals
- one universal Rust web framework;
- one universal service runtime or platform SDK;
- a giant generated control plane or hosted dashboard as the primary artifact;
- flattening HTTP surfaces, config surfaces, telemetry, async shutdown, and job semantics into one fake “service health” schema;
- pretending docs.rs output alone proves runtime support.

## Archive implications
- The archive should now treat **Service Surface + Runtime Settings + Observability + Async Reliability + Background Work + Support Envelope** as a coupled **Service Productization Stack** in frontier discussions.
- Future revisions should prefer **portable route/settings contracts, validated telemetry profiles, shutdown/work evidence, docs/support truth, and consumer proofs** over new framework wrappers, app templates, or “full platform” fantasies.
- The next credible move is now explicit: turn this stack plus the pilot program into the epic sketched in [`proposals/epic-service-productization-stack.md`](../proposals/epic-service-productization-stack.md), keeping the stack thin enough that service teams can import it without adopting one official framework.
- When Policy, Release Pipeline, Incident, DocProof, or Atlas work cites service readiness, they should import **service surface**, **settings truth**, **runtime evidence**, **async/work truth**, and **support truth** separately.

## References (signals)
- 2024 State of Rust survey results:
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust in 2026 / flagship themes:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Stabilize rustdoc `doc_cfg` feature:
  https://rust-lang.github.io/rust-project-goals/2025h2/rustdoc-doc-cfg.html
- docs.rs changed default targets:
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- Cargo development cycle 1.94:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- axum:
  https://docs.rs/axum/latest/axum/
- tower-http:
  https://docs.rs/tower-http/latest/tower_http/
- tracing:
  https://docs.rs/tracing
- config:
  https://docs.rs/config/latest/config/
- apalis:
  https://docs.rs/crate/apalis/latest
