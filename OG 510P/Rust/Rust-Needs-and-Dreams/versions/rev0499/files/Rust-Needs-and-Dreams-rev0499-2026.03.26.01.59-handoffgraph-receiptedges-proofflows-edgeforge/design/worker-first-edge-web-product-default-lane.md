# Design: Worker-first edge web product default lane (provider/runtime truth + storage/binding truth + route/assets/deploy truth)

## Goal
Add the first maintained **worker-first edge web-product** defaults-corpus card so the archive can answer a recurring practical question:
**what should a serious Rust-involving edge-hosted web/API product normalize around right now if the team wants the clearest boring default?**

This lane should not replace the broader `design/web-productization-stack.md`.
It should give that stack one bounded maintained answer for a very common project class.

## Why this note is needed now
The archive already has three maintained public-web lanes:
- browser-first public web app;
- full-stack Rust web product;
- browser-consumed Wasm package.

But it still lacked a maintained answer for **worker-first edge-hosted products** where the real substrate is not “a Rust web server you own” but a provider-managed request/runtime platform with explicit bindings, route/domain configuration, deployment/version surfaces, and product-specific limits.

That omission is harder to justify now because:
- Rust’s March 20, 2026 challenges post still frames ecosystem navigation as a problem of **choice paralysis** and **tacit knowledge**;
- the 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated workflows rise;
- Cloudflare now has first-party Rust support docs for Workers, including template generation, local development, bundling, and deployment through Wrangler;
- Cloudflare’s current docs make bindings, service bindings, routes, assets, version metadata, and runtime limits explicit enough to support a bounded lane rather than leaving it as folklore;
- `workers-rs` has become broad enough to expose serious product primitives, but its own docs still keep rough edges visible, including experimental RPC/client-binding generation and a testing story that often still routes through Miniflare/JS;
- Fastly Compute remains a serious Rust lane, but its own docs explicitly pin platform-supported Rust versions and note that some guide material may lag the latest SDK;
- Spin remains a serious alternative when portability, multi-trigger composition, and mocked Wasm-native testing matter more than a managed global edge network;
- and the repo’s current public-web split is incomplete if “full-stack web” and “edge worker product” stay blurred together.

Together those signals say the next worthy move is **not** another generic edge/serverless essay.
It is a bounded boring default card.

## Chosen project class
The first edge card should cover:
- products whose primary execution substrate is a provider-managed worker/edge runtime rather than a self-managed Rust server;
- APIs, lightweight request transforms, authenticated edges, soft-state products, queue/cron-adjacent edges, and asset-plus-worker products where route/domain and provider bindings are first-class;
- teams that want serious Rust in the request/runtime layer and are willing to accept provider-managed platform boundaries;
- products where binding/env truth, version/deploy truth, runtime-envelope truth, and portability caveats matter alongside handler code.

It should **not** try to cover in one card:
- ordinary regional/full-stack Rust hosting where Axum/Actix plus a deploy target is the real center;
- browser-first web apps or npm/browser package publication;
- portable self-hosted Wasm application hosts where the main goal is provider independence;
- or “Rust as a helper module behind a JS/TS edge host,” which is closer to a package/component lane than to a product-runtime lane.

## Default thesis
For this bounded project class, the conservative default should currently be:

**Cloudflare Workers + `workers-rs` + Wrangler**, with explicit acceptance of provider-managed bindings and route/domain/assets configuration, and with the internal-service boundary starting from HTTP/service bindings rather than assuming typed Rust RPC is already the boring default.

Why this is the right first card:
- Cloudflare has first-party Rust guidance, not just community examples.
- The runtime surface is broad and explicit: bindings to platform products, route/domain configuration, assets, service bindings, and version metadata are all documented product surfaces.
- The local-dev and deploy loop is unusually legible through Wrangler.
- Limits are clearly documented, which keeps the lane honest.
- The card stays honest about provider lock instead of pretending “edge” is a portable generic host today.

## Serious alternatives that must stay visible
### 1. Fastly Compute + `fastly`
This wins when CDN/proxy/request-manipulation depth, Fastly-specific edge control, or its Wasmtime-based Compute environment is central enough to justify explicit platform/version constraints.

### 2. Spin + Rust components
This wins when portability, self-hosting, component-style composition, mixed triggers, and Wasm-native mocked tests matter more than the tight integration of one managed edge network.

## What the card must keep separate
The maintained card should visibly preserve:
- **provider/runtime envelope truth**;
- **binding/storage/service truth**;
- **route/domain/assets/deploy truth**;
- **local-dev/testing truth**;
- **portability/provider-lock truth**;
- **support/docs truth**;
- and **lane judgment** versus project-specific escalation.

## Non-goals
- declaring one “serverless” or “edge” winner for every Rust deployment story;
- pretending full-stack origin hosting and worker-first edge hosting are the same lane;
- pretending typed multi-service Rust RPC on Workers is already the boring default;
- or turning the corpus into a provider benchmark scoreboard.

## Archive implications
- Add a first maintained worker-first edge-product card under `defaults/`.
- Add a first renewal receipt under `evidence/`.
- Refresh corpus/frontier/meta files so the repo treats **worker-first edge product** as a maintained public lane distinct from **browser app**, **full-stack web product**, and **browser package**.
- Keep the new separate **portable self-hosted Wasm edge host** card distinct from the managed-provider worker-runtime card, and keep future narrower cards available such as a **JS/TS host + Rust package** overlay if the evidence warrants them later.

## References
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cloudflare Workers Rust support:
  https://developers.cloudflare.com/workers/languages/rust/
- Cloudflare Workers limits:
  https://developers.cloudflare.com/workers/platform/limits/
- Cloudflare Workers bindings:
  https://developers.cloudflare.com/workers/runtime-apis/bindings/
- Cloudflare Service bindings:
  https://developers.cloudflare.com/workers/runtime-apis/bindings/service-bindings/
- Cloudflare routes:
  https://developers.cloudflare.com/workers/configuration/routing/routes/
- Cloudflare static assets binding:
  https://developers.cloudflare.com/workers/static-assets/binding/
- Cloudflare version metadata:
  https://developers.cloudflare.com/workers/runtime-apis/bindings/version-metadata/
- `workers-rs` docs:
  https://docs.rs/worker/latest/worker/
- Fastly Rust on Compute:
  https://www.fastly.com/documentation/guides/compute/developer-guides/rust/
  https://www.fastly.com/documentation/guides/compute/getting-started-with-compute/
- Spin triggers and testing:
  https://spinframework.dev/v3/triggers
  https://spinframework.dev/v3/testing-apps
