# Default card: Conservative browser web app (2026 Q1)

Latest renewal receipt: `evidence/conservative-browser-web-app-2026Q1-renewal-2026-03-22.md`

## Scope
This card applies to:
- browser-first Rust web applications rendered in the browser;
- teams that want a boring static-hosted or CDN-hosted app lane rather than a full-stack framework commitment on day one;
- products that may call an API but do not need Rust-owned SSR as the default assumption;
- teams that want explicit bundle/base-path/deploy posture rather than bundler folklore.

Assumptions:
- stable Rust;
- browser-first support scope;
- static asset deployment is acceptable;
- JavaScript bootstrapping is acceptable because the browser-Wasm app is loaded through generated JS;
- the team wants a path that can later escalate to SSR or other modes without starting from raw JS interop.

This is **not** the default for:
- full-stack SSR/hydration products where Rust should own both browser and server halves;
- npm-published Wasm packages or JS-interop-heavy libraries;
- cross-platform one-codebase ambitions spanning web + desktop + mobile;
- browser-worker / edge-runtime products as the primary lane;
- or projects whose main constraint is deep JavaScript ecosystem interop rather than browser app productization.

## Why this default now
Rust’s latest challenges framing still says ecosystem navigation is burdened by **choice paralysis** and **tacit knowledge**.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated workflows rise.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

The 2024 State of Rust survey says WebAssembly usage is mostly in the **browser** (23%) rather than other Wasm contexts (7%), which means browser-facing Wasm is a mainstream Rust lane.
https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/

Leptos’s current book now makes the split unusually explicit: **CSR with Trunk** is the browser-first lane, while **SSR with `cargo-leptos`** is a separate full-stack lane. Its docs also spell out the real tradeoffs: CSR gives faster builds, simpler deployment, and a simpler mental model, while SSR improves initial-load and SEO behavior; CSR apps use generated JS to load the Wasm bundle; and deployment/base-path details are part of the product story.
https://book.leptos.dev/getting_started/index.html
https://book.leptos.dev/deployment/csr.html
https://book.leptos.dev/deployment/ssr.html

Trunk now provides the clearest boring bundling/deploy contract for this scope. It builds, bundles, and ships assets through a minimal-config HTML entrypoint, and its build outputs are ready to serve from `dist/`.
https://trunkrs.dev/

The serious alternatives are real enough that the default must stay bounded:
- Dioxus explicitly treats full-stack/server-client split, route bundle splitting, asset/CDN posture, and deployment as part of one framework story.
  https://dioxuslabs.com/learn/0.7/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
- Yew remains a serious frontend option, and its SSR docs are explicit that browser APIs like `web_sys` are unavailable during server rendering.
  https://yew.rs/docs/advanced-topics/server-side-rendering
- `wasm-bindgen` and `wasm-pack` still make clear that **browser package / JS interop** is a different lane from a browser app product.
  https://rustwasm.github.io/docs/wasm-bindgen/
  https://rustwasm.github.io/docs/wasm-pack/introduction.html
  https://rustwasm.github.io/docs/wasm-pack/commands/build.html

For this exact project class, the archive’s current answer is:
**use Leptos in CSR mode with Trunk as the conservative default for browser-first Rust web apps, keep render mode explicit, keep bundle/base-path/deploy posture explicit, and escalate to Leptos SSR, Dioxus, Yew, or `wasm-pack` only when the product scope actually changes.**

## Decision label
**default-with-caveats**

It is the clearest boring default for this narrow browser-first scope, but it should not be widened into “the Rust web answer” in general.

## Default lane summary
### Default lane
- render mode: **CSR / browser-first**
- app framework: **Leptos**
- bundler / asset lane: **Trunk**
- browser capability posture: **prefer framework-native DOM/reactive patterns first; isolate `web-sys` and JS interop when needed**
- service/API posture: **separate API/service boundary; do not silently couple the card to Rust-owned SSR**
- deployment posture: **static-hosted / CDN-hosted assets with explicit base-path and release-build checks**

### Serious alternatives
- **Leptos SSR + `cargo-leptos`** when SEO, first paint, hydration, or Rust-owned backend logic are central.
- **Dioxus** when a unified app framework spanning web/full-stack and possibly desktop/mobile is part of the product goal.
- **Yew** when the team wants a frontend-focused Rust component model without this card’s chosen framework path.
- **`wasm-pack` / raw `wasm-bindgen`** when the subject is actually a browser-consumed package or JS-interop-heavy library rather than a browser app product.

### Watch / not-default here
- **full-stack Rust web product** as a separate future card rather than a silent widening of this one.
- **browser package / npm-published Wasm library** as a separate future card rather than treating package publication as app deployment.
- **worker / edge-runtime web product** as a separate future card rather than collapsing runtime environments.

## Slot guidance
### Render-mode slot
Make `csr` an explicit product decision.
Do not start with browser-only rendering and then talk as if SSR/hydration is already owned.
If SEO, first-paint HTML, or server-authored initial state are central, leave this lane.

### Bundler / asset slot
Prefer **Trunk** for this lane because it gives the clearest HTML-entrypoint, asset, and `dist/` contract.
Do not hide base-path, asset-path, or static-host assumptions inside ad hoc shell scripts.

### Browser-capability / interop slot
Keep browser API use explicit.
Prefer framework-native patterns first; isolate `web-sys`, `wasm-bindgen`, and handwritten JS interop to the smallest boundary that needs them.
Do not let one browser API demo silently become the whole app contract.

### Service-boundary slot
Treat the API/service as a separate boundary.
This card is compatible with “browser app + existing backend/API”, but it is not the same thing as “Rust owns the server too.”

### Deployment / support slot
Deploy release builds only.
Keep non-root path, CDN, and static-host assumptions explicit.
Do not say “deployment is easy” without naming whether the app expects root-path hosting, client-side routing fallback, or runtime-injected origins/settings.

## Serious alternatives and when they win
### Leptos SSR wins when
- Rust should own both the browser and server halves;
- SEO and initial-load behavior matter enough to choose SSR intentionally;
- or the product needs hydration/islands/server functions as first-class design constraints.

### Dioxus wins when
- one-codebase ambitions across multiple client surfaces matter;
- full-stack/server-client split, bundle splitting, and asset/deploy posture should live inside one chosen framework story;
- and the team wants the Dioxus CLI/framework posture rather than this narrower browser-first lane.

### Yew wins when
- the team wants a frontend-focused Rust component model;
- the product is still primarily a browser app rather than a unified cross-platform app framework bet;
- and the team does not need the specific Leptos progression path.

### `wasm-pack` / raw `wasm-bindgen` win when
- the subject is really a library or package for JS/browser consumers;
- npm package identity and JS glue are part of the primary product surface;
- or the team needs lower-level interop more than a browser-app framework default.

## Escalate to a project-specific brief when
- SSR/hydration or server functions become central;
- base-path / multi-origin / auth / edge-runtime posture dominate deployment;
- the app needs deep JavaScript ecosystem interop or package publication;
- a cross-platform one-codebase ambition makes Dioxus or another framework a better fit;
- or browser-worker / media / canvas / custom capability constraints drive the design.

## Canonical references
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- 2024 State of Rust survey:
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- Trunk:
  https://trunkrs.dev/
- Leptos book / getting started:
  https://book.leptos.dev/
  https://book.leptos.dev/getting_started/index.html
  https://book.leptos.dev/view/index.html
- Leptos deployment:
  https://book.leptos.dev/deployment/index.html
  https://book.leptos.dev/deployment/csr.html
  https://book.leptos.dev/deployment/ssr.html
- Leptos SSR/hydration/islands:
  https://book.leptos.dev/ssr/21_cargo_leptos.html
  https://book.leptos.dev/ssr/22_life_cycle.html
  https://book.leptos.dev/ssr/24_hydration_bugs.html
  https://book.leptos.dev/islands.html
- Dioxus:
  https://dioxuslabs.com/learn/0.7/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
- Yew SSR:
  https://yew.rs/docs/advanced-topics/server-side-rendering
- wasm-bindgen:
  https://rustwasm.github.io/docs/wasm-bindgen/
- wasm-pack:
  https://rustwasm.github.io/docs/wasm-pack/introduction.html
  https://rustwasm.github.io/docs/wasm-pack/commands/build.html
  https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/index.html

## Renewal inputs
Recheck before renewal:
- whether **Leptos CSR + Trunk** still provides the clearest boring browser-first app lane;
- whether a **full-stack Rust web product** card should now split off and become central;
- whether Dioxus’s web/full-stack contract changes enough to move it upward for this scope;
- whether a clearer maintained **browser package / npm-published Wasm** card now deserves to split away;
- whether Trunk’s bundling/base-path/deploy posture changes materially;
- and whether browser capability / JS-interop expectations need stronger explicit hygiene in the card.

Signal refs:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://trunkrs.dev/
- https://book.leptos.dev/getting_started/index.html
- https://book.leptos.dev/deployment/csr.html
- https://book.leptos.dev/deployment/ssr.html
- https://dioxuslabs.com/learn/0.7/
- https://yew.rs/docs/advanced-topics/server-side-rendering
- https://rustwasm.github.io/docs/wasm-bindgen/
- https://rustwasm.github.io/docs/wasm-pack/introduction.html

## Non-goals
- choosing one Rust web framework for every web project;
- flattening browser-first app, full-stack app, and browser-package lanes into one card;
- hiding CSR tradeoffs around JS bootstrapping, initial load, or SEO;
- or replacing project-specific web-productization review.
