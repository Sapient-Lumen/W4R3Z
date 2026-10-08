# Gap: Worker-first edge products still lack a reviewable boring default for provider/runtime/state/route truth

## The missing thing
Rust now has several real edge-hosted stories, but the ecosystem still lacks a **reviewable boring default** for teams asking:
**how should we ship a serious worker-first edge product in Rust without turning every project into a provider-evaluation folklore exercise?**

## Why the gap is real
Current signals all point to the same missing layer:
- Rust’s official challenges framing still names **choice paralysis** and **tacit knowledge** in ecosystem navigation.
- Cloudflare now has first-party Rust docs for Workers, with a template, local dev, bundling, deployment, bindings, service bindings, routes, static assets, version metadata, and explicit limits.
- `workers-rs` exposes a serious product surface, but its docs still show that typed RPC/client binding generation is experimental and that end-to-end testing is not yet a pure-Rust everything story.
- Fastly Compute remains a serious Rust lane, but its docs explicitly pin supported Rust versions and admit that some guide material can lag the latest SDK.
- Spin remains a serious alternative when portability, multi-trigger composition, and mocked Wasm-native tests matter more than one provider’s managed edge network.

The ecosystem therefore does **not** mainly lack “another serverless framework”.
It lacks a portable way to keep the following truths reviewable at once:
- which provider/runtime actually owns request execution,
- which state/storage/binding primitives are first-class,
- how routes/domains/assets/versioning are carried,
- what the local-dev and testing story really is,
- where portability ends and provider lock begins,
- and when a product should remain worker-first rather than becoming an ordinary full-stack service.

## Why this deserves a maintained card instead of only a stack note
This project class recurs often.
Teams repeatedly ask some variant of:
- should we use Cloudflare Workers,
- Fastly Compute,
- Spin,
- or just run a normal Rust service somewhere close to users?

Without a bounded maintained answer, guidance collapses back into hype, provider familiarity, or one compelling demo.
That is exactly the kind of tacit-knowledge failure the archive is trying to reduce.

## Proposed correction
Publish a maintained defaults-corpus card for **worker-first edge web product** with:
- **Cloudflare Workers + `workers-rs` + Wrangler** as the conservative default for the narrow provider-managed edge-runtime scope;
- **Fastly Compute + `fastly`** and **Spin + Rust components** as explicit serious alternatives;
- a receipt that keeps provider/runtime envelope truth, binding/storage truth, route/assets/deploy truth, local-dev/testing truth, portability/provider-lock truth, and support/docs truth visibly separate.

## References
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://developers.cloudflare.com/workers/languages/rust/
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/workers/runtime-apis/bindings/
- https://developers.cloudflare.com/workers/runtime-apis/bindings/service-bindings/
- https://developers.cloudflare.com/workers/configuration/routing/routes/
- https://developers.cloudflare.com/workers/static-assets/binding/
- https://developers.cloudflare.com/workers/runtime-apis/bindings/version-metadata/
- https://docs.rs/worker/latest/worker/
- https://www.fastly.com/documentation/guides/compute/developer-guides/rust/
- https://www.fastly.com/documentation/guides/compute/getting-started-with-compute/
- https://spinframework.dev/v3/triggers
- https://spinframework.dev/v3/testing-apps
