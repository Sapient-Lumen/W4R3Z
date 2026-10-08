# Design: Service Surface Kit (`cargo servicecheck`, `service-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust service’s supported HTTP/application service surface: route identities, methods, path patterns, media types, middleware/runtime behavior, checked exchanges, and evidence that the declared service surface still matches the program.

This should **not** replace `axum`, `tower-http`, `hyper`, `actix-web`, `poem`, `utoipa`, `aide`, `poem-openapi`, `wiremock`, or gateway/proxy products.
It should make them compose better and make support claims reviewable.

## References (signals)
- The 2024 Rust survey says Rust is especially popular for server backends, web and networking services, and cloud technologies.
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- AreWeWebYet describes Rust web frameworks as mature and production ready, which means the missing seam is increasingly contract/review quality rather than bare capability.
  https://www.arewewebyet.org/
  https://www.arewewebyet.org/topics/frameworks/
- `axum` focuses on ergonomics/modularity and explicitly leans on `tower` + `tower-http` middleware.
  https://docs.rs/axum/latest/axum/
- `tower-http` provides HTTP-specific middleware and utilities compatible with frameworks that use `http`/`http-body`, including `hyper`, `tonic`, and `warp`.
  https://docs.rs/tower-http
- `axum` middleware docs explicitly call out common layers and middleware ordering.
  https://docs.rs/axum/latest/axum/middleware/index.html
- `tower-http` exposes concrete service-behavior seams such as CORS, tracing, metrics, request validation, timeouts, request IDs, and sensitive-header treatment.
  https://docs.rs/tower-http/latest/tower_http/cors/index.html
  https://docs.rs/tower-http/latest/tower_http/trace/index.html
  https://docs.rs/tower-http/latest/tower_http/metrics/index.html
  https://docs.rs/tower-http/latest/tower_http/sensitive_headers/index.html
- `utoipa`, `utoipa_axum`, `aide`, and `poem-openapi` show strong code-first OpenAPI lanes already exist.
  https://docs.rs/utoipa
  https://docs.rs/utoipa-axum
  https://docs.rs/aide/latest/aide/
  https://docs.rs/aide/latest/aide/axum/
  https://docs.rs/poem-openapi/latest/poem_openapi/
- `utoipa-swagger-ui` shows framework-bridged doc-serving already matters for service teams.
  https://docs.rs/utoipa-swagger-ui/latest/utoipa_swagger_ui/
- `wiremock` provides black-box HTTP mocking/testing for Rust applications interacting with third-party APIs.
  https://docs.rs/wiremock/

## Core components

### 1) `service-surface/v0`
A design-time declaration of the supported service boundary for a binary/service/workspace.

Required ideas:
- service identity (crate/workspace/service/deployment profile)
- protocol families in scope:
  - HTTP/1.1
  - HTTP/2
  - gRPC-over-HTTP as attachment/reference in v0 when present
  - upgrade/streaming lanes declared explicitly where relevant
- base URL/base path assumptions
- versioning/deprecation posture
- support classes:
  - `official`, `best-effort`, `experimental`, `deprecated`, `internal`
- environment/posture notes:
  - public internet
  - private/internal
  - admin-only
  - sidecar/local-only

This is the thing humans review before trusting automation.

### 2) `route-map/v0`
A portable map of supported operations.

Required ideas:
- stable route/operation identifiers
- method + path pattern
- path/query/header/body presence hints
- request/response media types
- streaming / SSE / websocket / upgrade markers where relevant
- linked attachments:
  - OpenAPI operation ids
  - Schema Contract ids
  - Identity/access requirement ids
  - Diagnostic ids or problem mappings
- support level per operation
- lifecycle posture:
  - current
  - deprecated
  - sunset planned
  - internal only
- optional semantic notes:
  - idempotent / retry-safe hints
  - pagination style
  - long-poll / callback / webhook lane

Design rule: preserve route identity even when a framework also has generated OpenAPI operation ids.

### 3) `service-middleware-profile/v0`
A machine-readable description of the HTTP/runtime behavior that surrounds the route map.

Required ideas:
- CORS policy posture
- timeout posture
- request-id generation/propagation
- body-size limits / request validation hooks
- compression/decompression posture
- path normalization / redirect behavior
- sensitive-header treatment
- trace/log correlation hooks where relevant
- panic/catch/failure-classification posture when exposed
- important middleware ordering assumptions
- declared gateway/proxy assumptions where known

This is the layer current schema tooling usually misses.

### 4) `exchange-catalog/v0`
Canonical example exchanges and negative-path examples.

Potential contents:
- request examples with headers/query/body
- expected response headers/status/media type/body class
- redirect examples
- error examples
- rate-limit / timeout / body-limit examples
- webhook/callback examples
- example provenance labels:
  - illustrative only
  - generated
  - checked in CI
  - captured from fixture replay

Design rule: keep examples small, stable, and clearly labeled. Do not dump production traffic.

### 5) `service-check-plan/v0`
A concrete plan for what is checked.

Required ideas:
- route inventory source(s): framework introspection / generated docs / manual declaration / test catalog
- selected deployment/runtime settings references
- checked environments/profiles
- checks performed:
  - route inventory extraction
  - OpenAPI/docs alignment
  - example exchange validation
  - middleware/header behavior checks
  - body-limit/timeout/CORS/request-id checks
  - deprecated/internal route coverage rules
- unsupported or intentionally omitted lanes

This is where the kit stops pretending “docs exist” means “service surface is reviewed.”

### 6) `service-check-report/v0`
Evidence from tests, docs comparisons, and runtime checks.

Possible contents:
- extracted route inventory summary
- undocumented route findings
- stale documented route findings
- operation/media-type mismatch findings
- CORS/header/request-id/body-limit/timeout check outcomes
- middleware-order hazard findings
- checked exchange pass/fail results
- drift findings between router/code/docs/examples
- support-level changes detected
- linked raw artifacts: OpenAPI documents, route dumps, HTTP transcripts, curl fixtures, HAR-like snippets

### 7) `service-diff-report/v0` (optional)
For compatibility-sensitive changes:
- route added/removed
- method changed
- path pattern changed
- media type changed
- status-behavior changed
- middleware behavior tightened/relaxed
- support class changed
- deprecation/sunset notes added or removed

Should distinguish:
- additive changes
- breaking changes
- policy/runtime tightening
- documentation-only drift
- manual rollout/gateway action required

### 8) `service-pack/v0`
Bundle format containing:
- `service-surface/v0`
- `route-map/v0`
- `service-middleware-profile/v0`
- optional `exchange-catalog/v0`
- one or more `service-check-report/v0`
- optional `service-diff-report/v0`
- optional raw attachments: OpenAPI docs, route inventories, contract-test fixtures, gateway config excerpts, and checked transcript artifacts

This is the unit that should travel through CI, docs, release review, and later archaeology.

### 9) `cargo servicecheck`
Reference UX:
- `cargo servicecheck init`
- `cargo servicecheck routes`
- `cargo servicecheck behavior`
- `cargo servicecheck examples`
- `cargo servicecheck diff`
- `cargo servicecheck pack`

`cargo servicecheck` should begin as an explainer / adapter / packer.
It should not pretend to be the one true framework or API gateway.

## Default policy
- **Separate route identity from schema attachments, middleware behavior, and checked exchanges.**
- **Preserve framework/router truth and generated-schema truth as attachments rather than flattening them into one fake model.**
- **Record middleware ordering assumptions explicitly** whenever they materially affect behavior.
- **Treat headers, limits, redirects, and request-id behavior as support surfaces**, not just implementation details.
- **Distinguish checked examples from illustrative examples** so docs stay honest.
- **Prefer HTTP-first v0 scope** and attach other protocol surfaces carefully instead of claiming universal service coverage immediately.

## What the kit should provide to others
- **Schema Contract Kit:** attach operation/schema artifacts to stable route ids without forcing OpenAPI to become the whole service contract.
- **Identity Surface Kit:** attach auth/access requirements to route ids while keeping the broader identity model separate.
- **Diagnostic Surface Kit:** map public service failures to diagnostic ids/problem details without flattening all runtime behavior into error schemas.
- **Runtime Settings Kit:** reference settings that affect base URLs, CORS, timeouts, header behavior, or body limits without absorbing runtime config itself.
- **Observability Kit:** align request-id/header propagation and trace/log fields with the declared service boundary without making telemetry the source of truth.
- **Support Envelope Kit:** express which target/runtime envelopes a given service profile is officially supported on.

## Overlap boundaries
- **Not another web framework:** routing ergonomics and request handling remain with `axum`, `poem`, `actix-web`, `hyper`, etc.
- **Not another OpenAPI generator:** `utoipa`, `aide`, `poem-openapi`, and friends remain the schema/document-generation lanes.
- **Not Schema Contract Kit:** data/schema compatibility remains separate; this kit focuses on the composed service boundary.
- **Not Identity Surface Kit:** auth/access policy attaches here by reference but remains a distinct artifact family.
- **Not Diagnostic Surface Kit:** failure codes and renderings remain separate even when linked to routes.
- **Not a gateway/service-mesh product:** the value is the artifact and review workflow, not a new control plane.

## Hard problems (explicitly scoped)
1. **Middleware ordering is real contract surface**
   - v0 should record declared ordering assumptions instead of pretending middlewares are commutative.
2. **Framework route inventories differ**
   - adapters should preserve raw framework truth and normalize identifiers carefully.
3. **OpenAPI is necessary but insufficient**
   - behavior such as CORS, timeouts, sensitive-header handling, or request-id propagation often lives outside the schema.
4. **Gateway/reverse-proxy behavior can blur ownership**
   - keep service-owned behavior distinct from external infra-owned behavior, but allow attachments/references.
5. **Non-HTTP protocols should not be faked in v0**
   - support careful attachment/extension paths instead of claiming every service shape is already unified.
