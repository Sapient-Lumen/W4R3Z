# Epic proposal: Web Productization Stack

## Thesis
Rust does not most urgently need another frontend framework, another bundler wrapper, or another “Rust for the web” comparison page.
It needs a **portable productization substrate for browser-facing products**.

The contribution should sit **above** existing serious lanes:
- browser API and JS interop via `wasm-bindgen` / `web-sys`,
- browser/package outputs via `wasm-pack`,
- HTML-entry bundling via Trunk,
- CSR/SSR/hydration/islands/full-stack lanes in frameworks like Leptos, Dioxus, and Yew,
- and deploy/support reality across static hosting, SSR services, and Wasm-based providers.

## The worthy contribution
A worthy contribution would make these truths reviewable and importable without forcing one framework or deployment lane:
1. **render-mode truth** — CSR, SSR, hydration, islands, SSG, mixed lanes;
2. **bundle/base-path truth** — Wasm/JS/CSS/assets/public URL/compression posture;
3. **browser capability truth** — `web-sys` features, JS glue, unstable API usage, worker/media/canvas/network assumptions;
4. **server/client split truth** — which code belongs to which target and why;
5. **deploy/package truth** — static-hosted bundle, service deployment, edge/Wasm deployment, npm/browser package lanes;
6. **support/docs truth** — browser/runtime floors, checked examples, and public promises.

This should look like a **thin artifact family** such as:
- `render-mode-brief/v0`
- `web-bundle-brief/v0`
- `browser-capability-brief/v0`
- `web-split-brief/v0`
- `web-consumer-handoff/v0`
- `web-product-pack/v0`

## Why this is ecosystem-shaping
This contribution would help at least five families at once:
- static browser Wasm apps,
- SSR/hydration apps,
- browser-facing Wasm packages published to npm,
- mixed full-stack Rust products,
- and support/release/deploy tools that currently have to reverse-engineer framework output and hosting conventions.

It would also create a cleaner import boundary for atlas/docs/editor/assistant consumers, which increasingly matter now that online docs remain canonical while machine-assisted consumption is rising.

## What this should not become
- not a universal frontend framework;
- not a universal bundler;
- not a framework ranking site;
- not a fake “web maturity” score;
- not a schema that erases the difference between browser packages, deployed apps, SSR services, and edge workers.

## Strong first proving grounds
1. a Trunk-style static CSR app with explicit route/base-path/bundle truth;
2. a Leptos-style SSR + hydration app with browser/server split truth;
3. a `wasm-pack` browser package with package-vs-app identity truth;
4. a Dioxus-style full-stack deploy lane with bundle splitting / asset / provider posture;
5. one checked support/docs consumer import showing browser/runtime-floor truth.

## References
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rustwasm.github.io/docs/wasm-bindgen/
- https://rustwasm.github.io/docs/wasm-bindgen/web-sys/index.html
- https://rustwasm.github.io/docs/wasm-pack/introduction.html
- https://trunkrs.dev/
- https://book.leptos.dev/getting_started/index.html
- https://book.leptos.dev/ssr/22_life_cycle.html
- https://dioxuslabs.com/learn/0.7/essentials/fullstack/
- https://yew.rs/docs/0.21/advanced-topics/server-side-rendering
