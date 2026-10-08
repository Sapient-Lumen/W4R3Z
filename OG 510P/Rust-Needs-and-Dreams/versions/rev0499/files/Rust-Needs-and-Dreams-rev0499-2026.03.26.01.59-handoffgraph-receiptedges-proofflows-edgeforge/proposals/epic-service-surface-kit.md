# Epic proposal: Service Surface Kit

## Thesis
Rust web/service development is mature enough that the missing contribution is no longer “yet another framework.”
The higher-leverage missing piece is a **portable service-surface contract** that lets teams declare, diff, validate, and ship what their service actually promises: route identities, methods, media types, middleware/runtime behavior, checked exchanges, and linked schema/auth/diagnostic evidence.

In other words: Rust needs a boring, attachable `service-pack/v0` more than it needs another thin framework wrapper with one team’s preferred defaults.

## Why now
The ecosystem signals line up:
- Rust is already heavily used for server backends, web and networking services, and cloud technologies.
- AreWeWebYet now frames Rust web frameworks as mature/production-ready.
- `axum` + `tower-http` already cover routing and reusable HTTP middleware well.
- code-first OpenAPI/documentation lanes already exist via `utoipa`, `utoipa_axum`, `aide`, and `poem-openapi`.
- black-box HTTP behavior testing already matters enough for tools like `wiremock`.

That means the missing substrate is not raw capability.
It is the **reviewable boundary above today’s pieces**.

Sources:
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://www.arewewebyet.org/
- https://docs.rs/axum/latest/axum/
- https://docs.rs/tower-http
- https://docs.rs/utoipa
- https://docs.rs/utoipa-axum
- https://docs.rs/aide/latest/aide/
- https://docs.rs/poem-openapi/latest/poem_openapi/
- https://docs.rs/wiremock/

## What should be built
A first credible version should ship:
1. `service-surface/v0`, `route-map/v0`, `service-middleware-profile/v0`, `exchange-catalog/v0`, `service-check-plan/v0`, `service-check-report/v0`, optional `service-diff-report/v0`, and `service-pack/v0`
2. adapters for common Rust service stacks (`axum`, `tower-http`, generated OpenAPI lanes, contract-test fixtures)
3. docs/reference generation for supported routes, support levels, example exchanges, and declared middleware/runtime behavior
4. validation/reporting support for route inventory drift, OpenAPI/docs mismatches, middleware/header/body-limit/CORS/request-id checks, and deprecated/internal route coverage
5. release/CI examples showing service packs attached to services, docs, and rollout review

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one `axum` + `tower-http` JSON API with route extraction, request-id propagation, CORS, timeout, and checked exchange examples
- one code-first OpenAPI service using `utoipa`/`aide` with docs/schema drift checks against route inventory
- one `poem-openapi` or alternative-framework pilot proving the artifacts are not `axum`-exclusive
- one service with reverse-proxy/gateway assumptions recorded explicitly to test ownership boundaries

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve route identity, attached operation/schema ids, and middleware-behavior claims
2. **v0.2 adapters**
   - support `axum`, `tower-http`, `utoipa`, `utoipa_axum`, `aide`, and contract-test attachments
   - support raw route inventory and generated-schema attachments without flattening either one
3. **v0.3 cross-kit integration**
   - integrate with Schema Contract, Identity Surface, Diagnostic Surface, Runtime Settings, Observability, and Support Envelope workflows
   - support diff/baseline workflows across releases and deployment modes
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact framework stack

## Success metrics
- Teams can review service-interface changes as explicit artifacts instead of reading router diffs and prose docs.
- Supported routes, media types, and middleware/runtime behavior remain documented from one declared source.
- Docs/OpenAPI examples become easier to trust because checked and illustrative material stay distinct.
- Framework migrations become easier because support claims survive beyond one router DSL.
- Rust services become easier to hand off to platform, gateway, docs, and client-generation workflows without bespoke glue.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Schema Contract Kit covers machine-readable schemas,
- Identity Surface Kit covers auth/access,
- Diagnostic Surface Kit covers failures,
- Runtime Settings Kit covers config,
- Observability Kit covers telemetry,
- and Support Envelope Kit covers platform/runtime baselines.

But none of those is the portable contract for the **composed service boundary itself**.
Service Surface Kit is the missing substrate that keeps those pieces attached to one reviewable application/service interface without absorbing them into one mega-format.
