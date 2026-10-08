# Gap: web apps, browser Wasm, and full-stack productization contracts

## What is missing
Rust now has a real web stack, but it still lacks a **portable productization layer for browser-facing products**.

Today there is no shared way to publish, exchange, and diff:
- the rendering mode a product actually supports (CSR, SSR, hydration, islands, SSG, mixed full-stack lanes),
- the browser/runtime surface it actually depends on (specific `web-sys` features, JS glue posture, browser-only APIs, worker/canvas/media/fetch assumptions, unstable Web APIs when used),
- the bundle and asset truth it actually ships (Wasm blobs, JS glue, CSS, route-split bundles, base-path/public-url assumptions, compression and caching posture),
- the browser-vs-server split it actually relies on (which code must stay off the browser target, which APIs are server-only, which interactions panic or degrade when rendered on the server),
- the package and deployment lanes it actually expects (static bundle, SSR service, npm-distributed Wasm package, edge/Wasm provider, CDN-hosted assets),
- and the support/docs claims that tell users which browsers, paths, runtimes, and deployment patterns are really supported.

That missing layer matters because the Rust web problem is no longer “can Rust run in the browser?”
The problem is “how does a Rust web product become a reviewable product instead of a pile of framework conventions, generated JS glue, bundle artifacts, deployment snippets, and README folklore?”

## The current seam is awkward
Rust already has strong web ingredients, but they stop short of a shared product boundary:
- the 2024 State of Rust survey says WebAssembly use is **mostly in browsers (23%) rather than other WebAssembly contexts (7%)**, which means browser-facing Wasm is not a niche corner of the ecosystem;
- `wasm-bindgen` explicitly treats high-level JS↔Wasm interop as a central Rust/WebAssembly lane, and `web-sys` exposes raw browser APIs behind cargo features instead of pretending there is one monolithic “browser runtime”;
- `wasm-pack` explicitly generates a JS wrapper, Wasm binary, README, and `package.json`, and documents npm publication as a first-class lane;
- Trunk already acts like a serious web bundler rather than just a “compile to Wasm” helper: it builds and bundles Wasm, JS snippets, and assets from an HTML entrypoint;
- Leptos explicitly offers at least two materially different starting lanes — browser CSR with Trunk, and SSR/hydration with `cargo-leptos` — and its docs spend real time on hydration bugs, route/path deployment, and Wasm binary-size optimization;
- Dioxus now openly treats route-level bundle splitting, CDN asset management, static site generation, and deployment to Wasm-based providers as part of its full-stack surface, while also warning that server-only dependencies can produce cryptic errors if they leak into the Wasm build;
- Yew’s SSR docs are explicit that browser APIs like `web_sys` are unavailable during server rendering and can panic if used there.

So the ecosystem is not missing one more frontend framework, one more HTML macro story, one more bundler, or one more “Rust React” comparison page.
It is missing the **boring contract/evidence layer that keeps rendering-mode truth, browser capability truth, bundle/deploy truth, server/client split truth, and support truth distinct while still letting them compose**.

## Why this matters
This gap matters because it cuts across multiple real Rust web families at once:
1. **browser-first Wasm apps** — bundle size, base paths, browser API features, and asset-loading posture shape whether the app is actually shippable;
2. **SSR + hydration apps** — client/server target splits, browser-only APIs, hydration boundaries, and deployment/runtime assumptions become part of the public contract;
3. **JS-interoperable Wasm packages** — npm package identity, JS wrapper provenance, browser-target settings, and support posture are product surfaces, not build trivia;
4. **full-stack Rust apps** — route rendering, server functions, asset/CDN policies, browser runtime floors, and support truth span both client and server lanes;
5. **support/release archaeology** — teams often cannot later answer what rendering mode was promised, what bundle was shipped, what path assumptions existed, what browser APIs were required, and what deployment lane was actually exercised.

A worthy contribution here is therefore not “a better Rust web framework.”
It is a shared way to make **Rust web products legible as products**.

## What “good” looks like
A worthy contribution here is **not** another giant abstraction crate.
It is a thin stack above the existing pieces:
- **Client App Surface Kit** for routes, app identity, browser-facing behavior, and page/runtime posture,
- **Service Surface Kit** for SSR/server-function/API/edge-server attachment lanes,
- **Runtime Settings Kit** for base URLs, API origins, feature toggles, env-driven deployment differences, and activation posture,
- **Host Package Kit** for npm/package identity and JS/Wasm package outputs where applicable,
- **Distribution Contract Stack** for static bundle vs service deployment vs package publication vs fallback/install truth,
- **Support Envelope + DocProof** for browser/runtime/support/docs truth,
- and one thin aggregate artifact such as `web-product-pack/v0` that references those lower-layer artifacts instead of erasing them.

That would let release tooling, deploy pipelines, docs, support, ecosystem-atlas work, and future editor/assistant consumers talk about the **same web product** without scraping framework templates and generated bundle directories.

## Sources
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://rustwasm.github.io/docs/wasm-bindgen/
- https://rustwasm.github.io/docs/wasm-bindgen/web-sys/index.html
- https://rustwasm.github.io/docs/wasm-bindgen/web-sys/using-web-sys.html
- https://rustwasm.github.io/docs/wasm-pack/introduction.html
- https://rustwasm.github.io/docs/wasm-pack/commands/build.html
- https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/packaging-and-publishing.html
- https://trunkrs.dev/
- https://book.leptos.dev/getting_started/index.html
- https://book.leptos.dev/ssr/22_life_cycle.html
- https://book.leptos.dev/ssr/24_hydration_bugs.html
- https://book.leptos.dev/deployment/binary_size.html
- https://book.leptos.dev/islands.html
- https://docs.rs/crate/leptos/latest
- https://docs.rs/crate/cargo-leptos/latest
- https://dioxuslabs.com/learn/0.7/essentials/fullstack/
- https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
- https://dioxuslabs.com/learn/0.7/guides/deploy/
- https://yew.rs/docs/0.21/advanced-topics/server-side-rendering
