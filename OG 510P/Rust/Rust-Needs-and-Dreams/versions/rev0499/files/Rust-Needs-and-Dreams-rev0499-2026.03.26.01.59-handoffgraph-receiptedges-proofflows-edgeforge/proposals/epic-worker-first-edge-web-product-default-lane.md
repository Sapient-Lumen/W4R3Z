# Epic proposal: Worker-first edge web product default lane

## Thesis
Add a maintained defaults-corpus card for **worker-first edge-hosted Rust web/API products** so the archive can answer a common practical question with a bounded current recommendation instead of only broad web/serverless theory.

## Proposed artifact family
- `design/worker-first-edge-web-product-default-lane.md`
- `defaults/conservative-worker-first-edge-web-product-2026Q1.md`
- `evidence/conservative-worker-first-edge-web-product-2026Q1-renewal-2026-03-22.md`
- frontier/meta refresh tying the new card back to `design/web-productization-stack.md`

## Initial lane judgment
For the narrow worker-first edge-product scope, publish:
- **Cloudflare Workers + `workers-rs` + Wrangler** as the conservative default;
- **Fastly Compute + `fastly`** and **Spin + Rust components** as serious alternatives for different scopes;
- explicit separation of provider/runtime envelope truth, binding/storage/service truth, route/assets/deploy truth, local-dev/testing truth, portability/provider-lock truth, and support/docs posture.

## Why this is epic-worthy
- It turns an older edge/serverless frontier into a reusable current answer.
- It covers a recurring real adoption lane rather than an edge case.
- It gives the archive a way to talk honestly about edge-hosted Rust without pretending that “edge” is just ordinary full-stack hosting with different marketing.
- It is exactly the kind of contribution the ecosystem is currently missing: not another provider wrapper, but a reviewable boring default with the real product/runtime constraints left visible.

## Non-goals
- declaring one edge provider the universal winner;
- collapsing full-stack origin hosting, worker-first runtimes, browser packages, and portable Wasm hosts into one card;
- or replacing `design/web-productization-stack.md`.
