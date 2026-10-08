# Design: Web Productization Stack (Client App Surface + Service Surface + Runtime Settings + Host Package + Distribution Contract + Support Envelope)

## Goal
Turn Rust browser-facing products into a **portable productization stack** instead of leaving each project to express its web story as a tangle of render-mode flags, Wasm bundles, JS wrappers, browser-feature cargo flags, SSR conventions, deploy snippets, and support folklore.

The stack should **not** replace Leptos, Dioxus, Yew, Trunk, `wasm-bindgen`, `wasm-pack`, SSR frameworks, or JS packaging tooling.
It should make them compose better and make supported web behavior reviewable.

## Why this note is needed now
Rust’s current signals say the missing problem is no longer “can Rust target the web?”
They say the missing problem is **what a Rust web product can honestly claim to support**:
- the 2024 State of Rust survey says WebAssembly use is mostly in the **browser** (23%) rather than non-browser contexts (7%), which makes browser-facing Wasm a mainstream product lane rather than a side quest;
- `wasm-bindgen` explicitly sits at the center of Rust↔JavaScript interop, while `web-sys` exposes browser APIs as cargo-feature-gated surfaces rather than pretending “the browser” is one uniform capability set;
- `wasm-pack` already turns a Rust crate into an npm-shaped output with Wasm, JS glue, README, and `package.json`, which means package identity and host-package truth already matter;
- Trunk already treats HTML entrypoints, JS snippets, Wasm blobs, and static assets as one bundling lane;
- Leptos explicitly splits CSR-with-Trunk from SSR/hydration-with-`cargo-leptos`, documents page-load and hydration mechanics, and treats binary size, path deployment, and server/client target separation as real concerns;
- Dioxus already treats route bundle splitting, asset/CDN handling, SSG, and deployment to Wasm-based providers as part of the product story, while warning that server-only dependencies leaking into browser builds produce cryptic failures;
- Yew’s SSR docs are explicit that `web_sys` APIs are unavailable on the server side and can panic if used there.

Together, those signals argue that the missing contribution is **not** another Rust web framework, another bundler, or another “just ship it to Wasm” wrapper.
It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Client App Surface: page, route, render-mode, and browser-facing behavior truth
Client App Surface owns the **declared browser-facing application boundary**:
- app identity and route families,
- render mode (`csr`, `hydrate`, `ssr`, `islands`, `ssg`, mixed full-stack lanes),
- page/head/base-path assumptions,
- browser event/lifecycle expectations,
- and checked browser-facing behavior.

This layer answers questions like:
- “Is this app actually browser-first, SSR-first, or mixed?”
- “Which routes/pages are part of the product surface?”
- “What path and page-load assumptions are official?”

Design rule: **render mode must not remain an implicit framework template choice**.

### 2) Service Surface: server attachments, SSR endpoints, and browser↔server boundaries
Serious Rust web products often have a server half.
Service Surface owns:
- SSR/server-render endpoints,
- server-function/API attachment lanes,
- browser-vs-server code boundaries,
- edge/service/runtime roles,
- and checked request/response behavior where the web product depends on it.

This layer answers questions like:
- “What part of this product requires a server at all?”
- “Which interactions are static, hydrated, server-rendered, or API-backed?”
- “What part of the app must never be compiled for the browser target?”

Design rule: **browser truth and service truth travel together, but they are not the same contract**.

### 3) Runtime Settings: base URL, origin, feature, and activation truth
Real web products change behavior through settings:
- public/base paths,
- API and asset origins,
- runtime feature toggles,
- environment-driven differences between local/dev/prod/preview,
- cache/profile/debug posture,
- and browser/runtime activation assumptions.

This layer answers questions like:
- “Why does this app only work under this path or origin?”
- “Which env values materially change the browser or SSR story?”
- “What settings are part of the supported product contract?”

Design rule: **deployment env and path assumptions are product truth, not only CI or hosting trivia**.

### 4) Host Package: JS/Wasm package identity and interop truth
Not every Rust web product ships only as an app bundle.
Some ship as browser-consumed Wasm/JS packages.
Host Package owns:
- npm/package identity when relevant,
- generated JS wrapper and type-definition provenance,
- Wasm package output identity,
- package-vs-app distinctions,
- and host-package support posture.

This layer answers questions like:
- “Is this a web app, a browser package, or both?”
- “What was actually generated for JS consumers?”
- “Which support claims apply to package consumers versus deployed apps?”

Design rule: **browser-package truth must not collapse into crate identity or bundle directories**.

### 5) Distribution Contract: shipped bundles, static hosting, service deploys, and receipts
Web products have multiple shipping lanes:
- static-hosted bundles,
- SSR/container/service deploys,
- edge/Wasm-provider deploys,
- npm/browser package publication,
- CDN asset posture,
- and install/deploy receipts or bundle manifests.

This layer answers questions like:
- “What was actually shipped?”
- “Was this deployed as static files, a service, an edge/Wasm worker, or a published package?”
- “Which path, asset, or fallback assumptions were exercised in the shipped lane?”

Design rule: **generated bundles and deployed products are related but not identical truths**.

### 6) Support Envelope + DocProof: browser floors, docs truth, and public promises
Support Envelope and DocProof together own:
- supported browsers/runtime floors,
- browser API assumptions,
- SSR/runtime host assumptions,
- checked docs/examples,
- path/deploy caveats,
- and public support posture.

This layer answers questions like:
- “Which browsers and runtime conditions are really supported?”
- “Did the docs match the render/deploy story?”
- “What can support and release teams safely promise?”

Design rule: **one successful demo deploy, one homepage bullet list, or one framework example is not the support contract**.

### 7) Downstream consumers
The stack becomes ecosystem-shaping when real consumers can import it honestly:
- **release/deploy** consumers can attach render-mode, bundle, deploy, and support truth;
- **support/incident** consumers can answer whether a failure belongs to browser capability, SSR split, bundle path, deploy mode, or support posture;
- **atlas/learning** consumers can compare serious Rust web lanes without pretending one framework has already won;
- **editor/assistant/docs** consumers can summarize web products without guessing from generated files and framework defaults.

Design rule: **consumers import selected web-productization facts; they do not redefine the stack**.

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust web stack.”
It is a portable boring stack with clear boundaries:

1. **render-mode and route truth first**
   - prove stable product identity, routes, page/load assumptions, and render-mode declarations on one real web app;
2. **bundle/base-path/deployable artifact truth second**
   - make Wasm/JS/CSS/assets/public-path posture reviewable instead of hidden in bundler defaults;
3. **browser capability and interop truth third**
   - preserve `web-sys` feature choices, JS glue posture, unstable API usage, and browser-only assumptions explicitly;
4. **server/client split and runtime-setting truth fourth**
   - prove SSR/hydration/service-boundary and path/origin/env activation can be captured honestly;
5. **support/docs and release/deploy consumers fifth**
   - prove browser floors, checked docs, deploy lanes, and package/app identities can be imported without re-deriving them.

An eventual aggregate artifact may exist, but it should be a **thin pack of linked artifacts**, not a mega-schema that erases render mode, browser capability, bundle/deploy truth, service boundaries, and support truth.

## Ranked first execution lanes
1. **static CSR bundle lane**
   - best first exporter because it proves page/load/base-path/bundle truth without immediately requiring SSR orchestration.
2. **SSR + hydration lane**
   - proves browser-vs-server boundary truth and hydration/runtime assumptions are part of the product contract.
3. **browser capability / JS interop lane**
   - proves `web-sys` feature posture, JS glue, and package/app boundary truth matter above framework code.
4. **full-stack deploy lane**
   - proves service attachment, asset origin, preview/prod differences, and deploy receipts matter as much as bundles.
5. **support/docs consumer lane**
   - proves browser/runtime-floor truth and checked docs are importable by support and release consumers.

## Non-goals
- one universal frontend framework;
- one universal bundler;
- one fake “Rust web maturity” score;
- flattening render mode, browser capability, bundle/deploy truth, service boundaries, and support truth into one readiness blob;
- pretending browser-Wasm packages, deployed apps, and SSR services are the same lane.

## Archive implications
- The archive should now treat **Client App Surface + Service Surface + Runtime Settings + Host Package + Distribution Contract + Support Envelope** as a coupled **Web Productization Stack** in frontier discussions.
- Future revisions should prefer **render-mode truth, browser capability truth, bundle/base-path/deploy truth, server/client split truth, and support/docs truth** over new frontend bake-offs, bundler wrappers, or framework-scorecard pages.
- When Client, Service, Distribution, Polyglot, Wasm, or Support work cites a Rust web product, it should import **render truth**, **browser/runtime truth**, **bundle/deploy truth**, **service-boundary truth**, and **support truth** separately.

## References (signals)
- 2024 State of Rust survey results:
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- wasm-bindgen + web-sys:
  https://rustwasm.github.io/docs/wasm-bindgen/
  https://rustwasm.github.io/docs/wasm-bindgen/web-sys/index.html
  https://rustwasm.github.io/docs/wasm-bindgen/web-sys/using-web-sys.html
  https://rustwasm.github.io/docs/wasm-bindgen/web-sys/unstable-apis.html
- wasm-pack:
  https://rustwasm.github.io/docs/wasm-pack/introduction.html
  https://rustwasm.github.io/docs/wasm-pack/commands/build.html
  https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/packaging-and-publishing.html
- Trunk:
  https://trunkrs.dev/
- Leptos + cargo-leptos:
  https://book.leptos.dev/getting_started/index.html
  https://book.leptos.dev/ssr/22_life_cycle.html
  https://book.leptos.dev/ssr/24_hydration_bugs.html
  https://book.leptos.dev/deployment/binary_size.html
  https://book.leptos.dev/islands.html
  https://docs.rs/crate/leptos/latest
  https://docs.rs/crate/cargo-leptos/latest
- Dioxus:
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
  https://dioxuslabs.com/learn/0.7/guides/deploy/
- Yew SSR:
  https://yew.rs/docs/0.21/advanced-topics/server-side-rendering
