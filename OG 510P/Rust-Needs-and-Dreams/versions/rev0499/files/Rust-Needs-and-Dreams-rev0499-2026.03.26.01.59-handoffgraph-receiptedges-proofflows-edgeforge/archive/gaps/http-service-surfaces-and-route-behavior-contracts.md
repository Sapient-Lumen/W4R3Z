# Gap: HTTP service surfaces and route-behavior contracts

## What is missing
Rust has mature web/service frameworks and strong HTTP building blocks, but it still lacks a **shared service-surface contract**.

Today there is no standard way to describe, exchange, diff, and review:
- which routes/endpoints a service actually supports,
- which methods, path patterns, media types, and status classes belong to that support promise,
- which middleware behaviors are part of the contract (CORS, timeouts, request IDs, body limits, compression, sensitive-header handling, path normalization, etc.),
- which operations are officially supported versus experimental/internal/deprecated,
- which example exchanges and negative paths were actually checked,
- and what evidence exists that the declared route/middleware/docs surface still matches the shipped service.

That missing layer matters because Rust is already widely used for server backends, web and networking services, and cloud-adjacent work. The ecosystem is strong enough that the weak point is no longer “can I build a service?” but “can I state and review what this service actually promises?”

Sources:
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://www.arewewebyet.org/
- https://www.arewewebyet.org/topics/frameworks/
- https://docs.rs/axum/latest/axum/
- https://docs.rs/tower-http
- https://docs.rs/utoipa
- https://docs.rs/aide/latest/aide/
- https://docs.rs/poem-openapi/latest/poem_openapi/
- https://docs.rs/wiremock/

## The current seam is awkward
The ecosystem clearly has ingredients:
- `axum` provides ergonomic routing/extractors and explicitly leans on the `tower` + `tower-http` middleware ecosystem,
- `tower-http` provides reusable HTTP middleware across frameworks using `http`/`http-body` abstractions,
- `axum`’s middleware docs explicitly call out common layers such as tracing, CORS, compression, request IDs, and timeouts, plus the importance of middleware ordering,
- `utoipa`, `utoipa_axum`, `aide`, and `poem-openapi` show that code-first OpenAPI generation is already a serious lane in Rust,
- and `wiremock` shows that black-box HTTP behavior checks already matter in practice.

But each real service still hand-assembles its support story out of:
- framework route declarations,
- middleware stacks and ordering,
- OpenAPI fragments or generated docs,
- ad hoc examples or cURL snippets,
- reverse-proxy/gateway assumptions,
- integration tests proving some happy/negative paths,
- and prose about rate limits, timeouts, body-size limits, or deprecation/versioning policy.

The result is not that Rust lacks web crates.
The result is that there is no portable way to say:
- “these are the supported operations and route identities,”
- “these are the media types and protocol assumptions,”
- “these middleware behaviors are part of the service contract,”
- “these auth/error/schema artifacts attach to these operations,”
- or “these example exchanges and route behaviors were actually checked.”

OpenAPI helps, but it does not fully solve the service-support problem by itself. Middleware order, timeout posture, request-id propagation, body limits, sensitive-header treatment, and other behavior often live outside the generated schema surface. That is exactly the pattern this archive should care about: strong parts, weak shared boundary.

Sources:
- https://docs.rs/axum/latest/axum/
- https://docs.rs/axum/latest/axum/middleware/index.html
- https://docs.rs/tower-http
- https://docs.rs/tower-http/latest/tower_http/cors/index.html
- https://docs.rs/tower-http/latest/tower_http/sensitive_headers/index.html
- https://docs.rs/utoipa
- https://docs.rs/utoipa-axum
- https://docs.rs/aide/latest/aide/
- https://docs.rs/aide/latest/aide/axum/
- https://docs.rs/poem-openapi/latest/poem_openapi/
- https://docs.rs/wiremock/

## Why this matters
This gap is bigger than “better web docs.”
It affects:
1. **compatibility review** — route removals, method changes, media-type changes, timeout/body-limit tightening, or changed middleware order can be real breaking changes;
2. **framework portability** — teams should be able to preserve the supported service surface while moving between `axum`, `poem`, `actix-web`, `hyper`, or gateway/front-door choices;
3. **documentation quality** — generated OpenAPI, example traffic, and runtime behavior drift unless they are tied to one declared model;
4. **security + ops clarity** — CORS, request-id propagation, sensitive-header treatment, and route normalization are support claims, not just local implementation details;
5. **testing realism** — many teams have route tests or schema tests, but not one portable artifact saying which service behaviors were checked;
6. **ecosystem composition** — Schema Contract Kit, Identity Surface Kit, Diagnostic Surface Kit, Runtime Settings Kit, Observability Kit, and Support Envelope Kit all need a coherent service boundary without owning it.

Rust service stacks are mature enough that the service interface itself is now part of the product/support contract. The ecosystem still treats that contract as scattered framework glue.

Sources:
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://docs.rs/axum/latest/axum/
- https://docs.rs/axum/latest/axum/middleware/index.html
- https://docs.rs/tower-http
- https://docs.rs/utoipa
- https://docs.rs/aide/latest/aide/
- https://docs.rs/wiremock/

## What “good” looks like
A worthy contribution here is **not** another web framework, another OpenAPI generator, or another integration-test helper.

It is a shared service-surface boundary:
- one `service-surface/v0` describing the supported service identity, protocol/base-path/versioning posture, and operation inventory,
- one `route-map/v0` giving stable route/operation identities, methods, path patterns, media types, support levels, and links to attached schema/auth/diagnostic artifacts,
- one `service-middleware-profile/v0` describing CORS, timeout, request-id, body-limit, compression, sensitive-header, path-normalization, and related HTTP behavior that is part of the support promise,
- one `exchange-catalog/v0` containing canonical example requests/responses and negative-path examples,
- one `service-check-plan/v0` describing route extraction, schema/docs comparison, middleware-behavior checks, and checked exchange coverage,
- one `service-check-report/v0` recording route coverage, drift findings, checked header/body/timeout/CORS/request-id behavior, and docs/OpenAPI mismatches,
- one optional `service-diff-report/v0` for route additions/removals, behavior tightening, deprecations, or support-level changes,
- and one `service-pack/v0` bundle for CI, docs, release review, and later archaeology.

That would let Rust teams treat the service interface as a reviewable support surface instead of a pile of router definitions, middleware layers, generated schema, and test folklore.
