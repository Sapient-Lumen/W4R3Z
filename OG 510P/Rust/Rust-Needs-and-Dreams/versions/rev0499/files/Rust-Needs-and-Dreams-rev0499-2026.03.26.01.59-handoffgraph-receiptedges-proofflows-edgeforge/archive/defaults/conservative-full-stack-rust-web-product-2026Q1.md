# Default card: Conservative full-stack Rust web product (2026 Q1)

Latest renewal receipt: `evidence/conservative-full-stack-rust-web-product-2026Q1-renewal-2026-03-22.md`

## Scope
This card applies to:
- Rust-owned web products where Rust should deliberately own both the browser and server halves;
- SSR plus hydration as a chosen part of the product model;
- teams willing to accept a dual-target Rust build;
- products that benefit from server functions and progressively-enhanced forms/actions;
- and web-first teams that want the clearest boring answer rather than immediate desktop/mobile convergence.

Assumptions:
- stable Rust;
- server-hosted deployment is acceptable;
- dual-target build coordination is acceptable;
- JavaScript bootstrapping is acceptable because hydration still depends on generated JS/Wasm in the browser;
- and the team wants one Rust-first product lane rather than a separate JS frontend and API backend by default.

This is **not** the default for:
- browser-first static-hosted apps whose backend is separate or already fixed;
- public API/service platforms where the UI is only one client among many;
- browser package / npm-published Wasm libraries;
- edge-worker/serverless-first products;
- or cross-platform one-codebase ambitions where web, desktop, and mobile should all be first-class from day one.

## Why this default now
Rust’s latest challenges framing still says ecosystem navigation is burdened by **choice paralysis** and **tacit knowledge**.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated workflows rise.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

The 2024 State of Rust survey says WebAssembly usage is mostly in the **browser** (23%) rather than other Wasm contexts (7%), which means browser-facing Wasm remains a mainstream Rust lane.
https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/

Leptos’s current book now makes the web split unusually explicit:
- **CSR with Trunk** is the browser-first lane;
- **SSR/full-stack with `cargo-leptos`** is the Rust-owned full-stack lane;
- SSR improves initial-load and SEO behavior but brings slower iteration and hydration complexity;
- and the browser/server product is really two builds coordinated together.
https://book.leptos.dev/getting_started/index.html
https://book.leptos.dev/ssr/index.html
https://book.leptos.dev/ssr/21_cargo_leptos.html
https://book.leptos.dev/ssr/22_life_cycle.html
https://book.leptos.dev/ssr/23_ssr_modes.html
https://book.leptos.dev/ssr/24_hydration_bugs.html

Leptos’s server-function and progressive-enhancement docs make the full-stack browser/server boundary concrete rather than magical:
- server functions are function-like RPC over ordinary web mechanisms;
- extractors can pull typed request data into server functions;
- redirects and response shaping stay server-visible;
- and `<ActionForm/>` enables progressively-enhanced form workflows that still work without JS/Wasm.
https://book.leptos.dev/server/25_server_functions.html
https://book.leptos.dev/server/26_extractors.html
https://book.leptos.dev/server/27_response.html
https://book.leptos.dev/progressive_enhancement/action_form.html

Axum remains the clearest conservative server choice for this lane because the current HTTP/service baseline is still unusually coherent around **Tokio + axum + typed extractors/state**.
https://docs.rs/axum/latest/axum/
https://docs.rs/axum/latest/axum/extract/
https://docs.rs/axum/latest/axum/struct.Router.html
https://docs.rs/axum/latest/axum/extract/struct.State.html

The serious alternatives are real enough that the default must stay bounded:
- Leptos itself still supports both **Axum** and **Actix Web** integrations on the server side.
  https://book.leptos.dev/getting_started/index.html
  https://book.leptos.dev/ssr/index.html
- Dioxus Fullstack treats the app as a client/server split, generates separate builds, and offers integrated middleware, websockets, authentication guidance, and native-client extension points.
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/server_functions/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/middleware/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/websockets/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/authentication/
- Cargo still makes features, workspaces, and config discovery part of the real build surface, which matters more, not less, when the product is two coordinated targets.
  https://doc.rust-lang.org/cargo/reference/features.html
  https://doc.rust-lang.org/cargo/reference/workspaces.html
  https://doc.rust-lang.org/cargo/reference/config.html

For this exact project class, the archive’s current answer is:
**use Leptos SSR + Axum + `cargo-leptos` as the conservative default for full-stack Rust web products, keep the two-build reality explicit, keep server-function versus public-API boundaries explicit, and escalate to Dioxus, Actix, browser-only CSR, or a split-frontend architecture only when the product scope actually changes.**

## Decision label
**default-with-caveats**

It is the clearest boring default for this narrow full-stack web scope, but it should not be widened into “the Rust web answer” in general.

## Default lane summary
### Default lane
- render/runtime posture: **SSR + hydration**
- app framework: **Leptos**
- server framework: **Axum**
- build coordinator: **`cargo-leptos`**
- browser/server boundary posture: **prefer server functions for first-party app flows; keep public/external APIs explicit when they are real product contracts**
- progressive-enhancement posture: **prefer form/action flows that degrade gracefully where appropriate**
- deployment posture: **release-only server + Wasm builds with explicit asset, origin, and base-path assumptions**
- shared-type posture: **prefer explicit shared models and fixed-width integers across wasm32/client ↔ server boundaries**

### Serious alternatives
- **Dioxus Fullstack** when one-codebase ambitions across web/desktop/mobile, integrated fullstack tooling, or framework-provided streams/websockets materially matter.
- **Leptos SSR + Actix Web** when local Actix expertise or existing Actix server shape is the better fit.
- **Conservative browser web app** when Rust should own the browser UI but not the server half by default.
- **Conventional split frontend + API** when JavaScript ecosystem interop, client-agnostic public APIs, or separate-team architecture dominates.

### Watch / not-default here
- **browser package / npm-published Wasm library** as a separate future card rather than treating npm publication as app deployment.
- **edge-runtime / worker-first web product** as a separate future card rather than collapsing runtime environments.
- **cross-platform full-stack app** as a different product ambition rather than a silent widening of this web-first lane.

## Slot guidance
### Dual-target build slot
Treat the app as **two coordinated builds**.
Do not let a CLI wrapper make the browser and server halves disappear conceptually.
Make target-specific features, server-only dependencies, and browser-only code paths explicit.

### SSR / hydration slot
Choose SSR and hydration intentionally.
Do not talk as if they are free wins.
If the product cannot tolerate slower iteration or hydration debugging, this may not be the right lane.

### Server-function / API slot
Prefer server functions for first-party application flows where the browser/server relationship is part of one product.
Do **not** silently turn every external integration, third-party consumer, or public contract into a framework-private server-function story.

### Shared-type slot
Keep shared models explicit.
Prefer fixed-width numeric types rather than `usize`/`isize` across wasm32/client and 64-bit server boundaries.

### Auth / session slot
Keep auth, session, cookie, and authorization posture explicit and server-owned.
This card does not treat framework choice as proof that auth is solved.

### Deployment / support slot
Deploy release builds only.
Keep static asset serving, base-path/origin assumptions, and container/VPS/server-host posture explicit.
Do not say “full-stack deploy is easy” without naming who serves assets, where cookies/sessions terminate, and how the browser finds the server origin.

## Serious alternatives and when they win
### Dioxus Fullstack wins when
- one-codebase ambitions across more than just the web are central;
- the team wants Dioxus CLI/tooling and its fullstack primitives as the primary framework story;
- integrated websockets/streams/native-client extension points are part of the product shape.

### Leptos + Actix wins when
- the team already has stronger Actix expertise or deployed server muscle there;
- server-side local fit beats the default’s Axum continuity;
- or the surrounding workspace already standardizes on Actix.

### Browser web app wins when
- the server half should remain separate or pre-existing;
- static-hosted/browser-first deployment is materially simpler;
- or the product does not really benefit from SSR/hydration and server functions.

### Conventional split frontend + API wins when
- the public API surface matters more than same-language app convenience;
- browser work needs much deeper JavaScript ecosystem interop;
- or organizational boundaries already treat frontend and backend as separate products.

## Escalate to a project-specific brief when
- auth/session/security posture dominates the design;
- the product needs multiple clients or a public API contract beyond the web app;
- edge/serverless runtime constraints dominate deployment;
- the product wants a cross-platform one-codebase story beyond the web;
- or the browser/server boundary includes specialized streaming, realtime, media, or compliance constraints.

## Canonical references
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- 2024 State of Rust survey:
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- Leptos book / getting started / SSR:
  https://book.leptos.dev/
  https://book.leptos.dev/getting_started/index.html
  https://book.leptos.dev/ssr/index.html
  https://book.leptos.dev/ssr/21_cargo_leptos.html
  https://book.leptos.dev/ssr/22_life_cycle.html
  https://book.leptos.dev/ssr/23_ssr_modes.html
  https://book.leptos.dev/ssr/24_hydration_bugs.html
- Leptos server / forms / responses:
  https://book.leptos.dev/server/25_server_functions.html
  https://book.leptos.dev/server/26_extractors.html
  https://book.leptos.dev/server/27_response.html
  https://book.leptos.dev/progressive_enhancement/action_form.html
- Leptos deployment:
  https://book.leptos.dev/deployment/ssr.html
  https://book.leptos.dev/deployment/binary_size.html
- Axum:
  https://docs.rs/axum/latest/axum/
  https://docs.rs/axum/latest/axum/extract/
  https://docs.rs/axum/latest/axum/struct.Router.html
  https://docs.rs/axum/latest/axum/extract/struct.State.html
- Dioxus full-stack:
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/server_functions/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/middleware/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/websockets/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/authentication/
- Cargo:
  https://doc.rust-lang.org/cargo/reference/features.html
  https://doc.rust-lang.org/cargo/reference/workspaces.html
  https://doc.rust-lang.org/cargo/reference/config.html

## Renewal inputs
Recheck before renewal:
- whether **Leptos SSR + Axum + `cargo-leptos`** still provides the clearest boring full-stack web answer;
- whether Dioxus fullstack or another lane has become a clearly better default for this exact scope;
- whether Cargo/config/workspace realities or browser/server target boundaries have shifted materially;
- whether auth/session/deploy guidance needs a sharper explicit overlay;
- and whether this lane now deserves to split further into **browser package / npm-published Wasm**, **edge-runtime**, or another narrower web card.

## Non-goals
- declaring Leptos SSR + Axum the universal Rust web answer;
- replacing explicit external/public API design with server-function convenience;
- solving auth, session, or compliance posture generically;
- or replacing project-specific deployment and security review.
