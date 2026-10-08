# Gap: browser web app defaults need render-mode, bundle, base-path, and browser-boundary truth

## What is missing
Rust’s web ecosystem is mature enough that teams can build serious browser-facing applications today, but it still lacks a **boring maintained default card** for one of the most common product shapes:
a browser-first web app compiled to Wasm and deployed as static assets.

The missing thing is not another framework.
The missing thing is a reviewable current answer to:
- what rendering mode should we assume;
- what bundling/deploy path should we start from;
- what browser capability/JS-interop boundary should stay explicit;
- when should we stay browser-first versus escalating to SSR/full-stack;
- and when is the subject actually a package-for-JavaScript rather than a browser app product?

## Why the gap is still real
Today the ecosystem already exposes all the ingredients, but still makes teams synthesize the product lane themselves:
- Rust’s 2026 challenges framing still says ecosystem navigation suffers from **choice paralysis** and **tacit knowledge**;
- the 2024 State of Rust survey says WebAssembly use is mostly **browser** use, which means this is not an edge lane;
- Trunk now gives a real HTML-entrypoint → bundle → `dist/` deployment story;
- Leptos explicitly separates CSR/Trunk from SSR/`cargo-leptos`, which proves “web app” is already multiple materially different lanes;
- Dioxus explicitly exposes bundle splitting, server/client split, and deployment posture as part of the framework contract;
- Yew’s SSR docs make browser-vs-server capability mistakes explicit;
- and `wasm-pack` still documents npm/browser package publication as a first-class workflow, which means app-product and package-product truths are not interchangeable.

## What a worthy contribution should look like
A worthy contribution here is not a framework bake-off.
It is a thin maintained lane that keeps these truths separate:
- **render mode**;
- **bundle/base-path/deploy posture**;
- **browser capability and JS interop**;
- **service/API boundary**;
- **support/docs truth**;
- and **project-specific escalation triggers**.

In practice, that means a maintained default card plus a renewal receipt, not only another strategic note.

## Sources
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://trunkrs.dev/
- https://book.leptos.dev/getting_started/index.html
- https://book.leptos.dev/deployment/csr.html
- https://book.leptos.dev/deployment/ssr.html
- https://book.leptos.dev/ssr/24_hydration_bugs.html
- https://dioxuslabs.com/learn/0.7/essentials/fullstack/
- https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
- https://yew.rs/docs/advanced-topics/server-side-rendering
- https://rustwasm.github.io/docs/wasm-bindgen/
- https://rustwasm.github.io/docs/wasm-pack/introduction.html
