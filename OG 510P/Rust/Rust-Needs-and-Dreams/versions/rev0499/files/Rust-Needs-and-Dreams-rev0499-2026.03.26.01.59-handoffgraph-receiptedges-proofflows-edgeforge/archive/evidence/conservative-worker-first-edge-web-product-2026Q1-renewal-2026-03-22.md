# Renewal receipt: Conservative worker-first edge web product (2026-03-22)

Card under review:
- `defaults/conservative-worker-first-edge-web-product-2026Q1.md`

Review goal:
- decide whether the archive should publish a first maintained **worker-first edge web product** card;
- decide whether the clearest boring current default is **Cloudflare Workers + `workers-rs` + Wrangler**;
- and keep provider/runtime envelope truth, binding/storage truth, route/assets/deploy truth, local-dev/testing truth, portability/provider-lock truth, and support/docs truth visibly separate.

## Canon import checked
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

## Fresh observations
1. Official Rust signals still say the ecosystem navigation problem is partly about **choice paralysis** and **tacit knowledge**, which supports publishing a bounded edge-worker default rather than leaving the lane to folklore.
2. Cloudflare’s current Rust docs now cover the entire create/dev/deploy loop through a single first-party path: template generation, Wrangler local development, Rust handler authoring, and deployment.
3. Cloudflare’s current platform docs make the worker-product surface broad and explicit enough to support a maintained card: bindings, service bindings, routes, assets, version metadata, and runtime limits are all first-class documented product surfaces.
4. Those same docs make the limits/provider truth impossible to ignore: the product surface is not “just a Rust server somewhere closer to users.” It is a managed runtime with explicit daily/subrequest behavior, route/domain modes, and binding-driven data/service access.
5. `workers-rs` is broad enough for real product work, but its docs still keep the sharp edges visible: RPC/client-binding generation is experimental, the WIT code generator is pre-alpha, and local end-to-end testing still often routes through Miniflare/JS rather than a pure-Rust testing story.
6. Fastly Compute remains a serious Rust lane, but its docs explicitly constrain the supported Rust-version window and note that some guide material can lag the latest SDK.
7. Spin remains a serious alternative because its docs make multiple triggers and mocked Wasm-native tests very legible, but that reads more like the strongest portability/composition/testing alternative than the broadest boring default for a managed edge-provider lane.

## Slot-by-slot review
### Provider/runtime envelope truth
Defaulting to **Cloudflare Workers** keeps the product in a clearly documented managed edge-runtime lane.
This is more honest for the bounded scope than pretending the runtime is just a generic Rust host with a CDN in front.

### Binding/storage/service truth
Defaulting to **platform bindings first** is supported by the current docs: bindings are documented as the primary way to reach platform resources and are explicitly described as having better performance and fewer restrictions than raw REST access from Workers.
That makes binding/env truth a first-class part of the lane rather than an optional convenience.

### Route/assets/deploy truth
Current Workers docs make routes, assets, worker-first asset execution, and version metadata explicit.
That supports keeping route/assets/version surfaces inside the lane rather than outside it as generic DevOps trivia.

### Local-dev/testing truth
Wrangler gives the clearest boring local-dev and deploy story for the lane.
However, `workers-rs` still keeps a caveat visible: end-to-end testing often still relies on Miniflare/JS.
That means the card should not over-claim a perfect Rust-only test story.

### Portability/provider-lock truth
This lane is intentionally provider-managed, so provider lock is not a hidden defect to erase from the card.
It is part of the lane truth.
That is also why **Spin** remains visible as a serious alternative rather than being flattened away.

## Serious alternatives retained
- **Fastly Compute + `fastly`** — strongest alternative when Fastly-specific edge/proxy control is strategic enough to justify tighter platform/version coupling.
- **Spin + Rust components** — strongest alternative when portability, self-hosting, multi-trigger composition, and mocked Wasm-native testing are central.

## Judgment
Publish the card as a maintained public default.

Label:
- **default-with-caveats**

Why:
- the project class recurs often;
- the corpus still lacked a maintained worker-first edge-runtime answer;
- and the evidence supports a bounded conservative default without pretending that edge hosting has already converged into one portable Rust lane.

## Replay notes
- renew when `workers-rs` testing or RPC/client-binding ergonomics materially improve;
- renew when Fastly Compute or Spin changes enough to challenge the boring default for this narrow scope;
- renew when Cloudflare’s route/assets/version/binding surfaces materially shift;
- keep the new **portable/self-hosted Wasm edge host** card distinct, and split again later only if the archive is ready for a separate **JS/TS edge host + Rust package** overlay.
