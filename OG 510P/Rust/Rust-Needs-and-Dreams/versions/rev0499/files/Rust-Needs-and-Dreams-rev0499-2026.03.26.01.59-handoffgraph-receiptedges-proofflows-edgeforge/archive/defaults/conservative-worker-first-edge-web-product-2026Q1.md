# Default card: Conservative worker-first edge web product (2026 Q1)

Latest renewal receipt: `evidence/conservative-worker-first-edge-web-product-2026Q1-renewal-2026-03-22.md`

## Scope
This card applies to:
- products whose primary execution substrate is a provider-managed worker/edge runtime rather than a self-managed Rust origin server;
- APIs, request transforms, auth edges, queue/cron-adjacent edges, and asset-plus-worker products where route/domain and platform bindings are first-class;
- teams that want serious Rust in the request/runtime layer and accept that provider/runtime boundaries are part of the product truth;
- products where limits, bindings, deploy/version surfaces, and portability caveats matter alongside handler code.

Assumptions:
- stable Rust;
- the team wants the clearest boring default for a **managed edge runtime** rather than the most portable host;
- the product can accept provider-managed route/domain/assets/binding configuration;
- the request/runtime layer is expected to own meaningful logic, not just a tiny helper module behind another primary host;
- provider lock should stay explicit rather than being hand-waved away.

This is **not** the default for:
- ordinary full-stack Rust hosting where Axum/Actix plus a deploy target is the real center;
- browser-first web apps or browser-consumed package publication;
- portable self-hosted Wasm hosts where independence from one provider is the main point;
- or “JS/TS host plus Rust helper package” architectures.

## Why this default now
Rust’s latest challenges framing still says ecosystem navigation depends too much on **choice paralysis** and **tacit knowledge**.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated learning rises.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Cloudflare now has first-party Rust support docs for Workers, including template generation, local development, bundling, and deployment via Wrangler.
https://developers.cloudflare.com/workers/languages/rust/

Cloudflare’s current docs also make the worker-product surface unusually legible: bindings, service bindings, routes, static assets, version metadata, and explicit limits are all first-class documented concepts.
https://developers.cloudflare.com/workers/runtime-apis/bindings/
https://developers.cloudflare.com/workers/runtime-apis/bindings/service-bindings/
https://developers.cloudflare.com/workers/configuration/routing/routes/
https://developers.cloudflare.com/workers/static-assets/binding/
https://developers.cloudflare.com/workers/runtime-apis/bindings/version-metadata/
https://developers.cloudflare.com/workers/platform/limits/

At the same time, current docs keep the caveats visible:
- `workers-rs` RPC/client-binding generation is still experimental and the WIT code generator is pre-alpha;
- local end-to-end testing still often routes through Miniflare/JS rather than a pure-Rust test story;
- Fastly explicitly constrains the supported Rust-version window on Compute;
- Spin’s strongest story is still portability/composition/testing rather than one provider’s globally managed edge network.

Those are exactly the conditions where a bounded default card is useful.

## Default lane
For this scope, default to:

**Cloudflare Workers + `workers-rs` + Wrangler**

Use it as:
- the primary request/runtime substrate;
- the primary deploy/version/config surface;
- the primary binding/env surface for edge-side data/services;
- and the default product shell when the team really wants a worker-first edge runtime, not just “something close to users”.

Label:
- **default-with-caveats**

## Core slot guidance
### Provider/runtime slot
Default to **Cloudflare Workers**.

Why:
- first-party Rust support docs;
- explicit worker template + local dev + deploy loop;
- clear documented bindings and runtime features;
- explicit runtime limits instead of hand-waved marketing;
- clear routes/assets/version surfaces that real products need.

### Rust runtime/API slot
Default to **`workers-rs`**.

Why:
- it is the first-party documented Rust path for Workers;
- it exposes the core runtime and binding APIs directly to Rust;
- it is broad enough for real product work.

Caveat:
- do **not** assume typed Workers RPC is already the boring default.
Start from ordinary request handlers plus documented bindings/service boundaries.
Treat `workers-rs` RPC and its experimental WIT/client-generation story as advanced material, not the lane baseline.

### Local-dev / deploy slot
Default to **Wrangler**.

Why:
- the Rust docs are already written around it;
- the create/dev/deploy loop is explicit;
- routes/assets/version metadata all live in the same operational surface.

### Binding/state slot
Default to **platform bindings first**, not raw external REST calls first.

Why:
- current Cloudflare docs explicitly say bindings provide better performance and fewer restrictions than REST APIs intended for non-Workers applications;
- the product surface is defined around bindings such as KV, R2, D1, Queues, Rate Limiting, and Service bindings.

### Edge decomposition slot
Default to **HTTP/service bindings and simple worker decomposition** before typed multi-service Rust RPC.

Why:
- Service bindings are first-class, documented, and zero-overhead on the platform;
- `workers-rs` RPC remains experimental enough that it should not be the boring baseline.

## Serious alternatives and when they win
### Fastly Compute + `fastly` wins when
- CDN/proxy/request-manipulation depth is the center of the product;
- Fastly-specific edge control is strategically valuable;
- or Wasmtime-backed Compute portability matters more than Cloudflare’s wider integrated binding surface.

Caveat:
- keep the explicit platform Rust-version support window in view.

### Spin + Rust components wins when
- portability and self-hosting matter more than one provider’s edge network;
- multi-trigger application composition is central;
- or Wasm-native mocked tests are important enough to outweigh managed-edge convenience.

## Escalate to a project-specific brief when
- the product is only edge-adjacent and a normal full-stack origin service may actually be the better center;
- provider lock, data locality, or compliance requirements dominate the architecture;
- the team is deciding among Cloudflare Workers, Fastly Compute, and Spin because all three genuinely fit;
- the product needs a richer state/coordination story than the conservative worker-first default comfortably covers;
- or the product wants typed multi-service RPC as a first principle.

## Canonical references
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cloudflare Workers Rust support:
  https://developers.cloudflare.com/workers/languages/rust/
- Cloudflare limits:
  https://developers.cloudflare.com/workers/platform/limits/
- Cloudflare bindings:
  https://developers.cloudflare.com/workers/runtime-apis/bindings/
- Cloudflare service bindings:
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

## Renewal inputs
Recheck before renewal:
- whether Cloudflare Workers + `workers-rs` still remains the clearest boring default for this worker-first edge scope;
- whether Fastly Compute or Spin changed enough to deserve a narrower but more central default card;
- whether `workers-rs` testing or RPC/client-binding ergonomics changed enough to move the decomposition guidance;
- whether Cloudflare limits, route/assets behavior, or version/deploy surfaces materially shifted;
- whether the boundary with **conservative portable self-hosted Wasm edge host** still reflects the real ecosystem split.

## Non-goals
This card is not:
- a universal edge/serverless verdict;
- a claim that “Rust web on the edge” has already converged everywhere;
- a replacement for project-specific portability/compliance review;
- or permission to smuggle an ordinary regional full-stack origin architecture into an edge-runtime card.
