# Design: Web Productization Pilot Program (Render Mode → Bundle/Base Path → Browser Capability → Server/Client Split → Support/Deploy Consumers)

## Goal
Turn the **Web Productization Stack** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable, ecosystem-shaping contribution that would materially improve how Rust web products are built, shipped, deployed, and supported?

The pilot program should not chase one framework winner.
It should sequence the contribution so each lane proves something concrete before the next lane widens scope.

## Why a pilot program is necessary
Rust web work is unusually easy to overread from demos.
A single successful page load can hide the things that actually determine whether a product is shippable:
- whether the app is CSR, SSR, hydration, islands, or a mixed lane,
- what Wasm, JS, CSS, and asset files actually ship,
- what browser APIs and cargo features are required,
- what code must stay out of the browser target,
- what base path, asset origin, and preview/prod settings materially change behavior,
- and what browsers and deployment lanes are really supported.

A credible plan therefore needs to decide:
- when render-mode truth is already enough,
- when bundle/base-path truth must be attached,
- when browser API and JS-interop posture become part of the contract,
- when server/client split evidence is required,
- and which support/deploy consumers justify graduation.

## Principles
1. **Start from page/render truth, not framework ideology**
   - a pack that proves how the product loads is worth more than another framework comparison chart.
2. **Keep render mode, browser capability, and deploy truth separate**
   - they travel together in real products, but they are not the same source of truth.
3. **Preserve browser-vs-server boundaries explicitly**
   - hydration bugs, server-only dependencies, and SSR panics happen where those boundaries blur.
4. **Treat bundle/base-path/origin assumptions as product truth**
   - users experience these as broken apps, not as bundler internals.
5. **Support claims need checked docs and receipts**
   - browser floors and deployment posture should graduate before big cross-platform claims do.
6. **Consumers import; they do not reinterpret**
   - release, support, docs, atlas, and assistant consumers should import artifacts instead of re-deriving the web story from build output directories.

## Common artifacts this program should drive
- `web-lane-brief/v0` — declare which pilot lane is being exercised, scope, targets, and non-goals.
- `render-mode-brief/v0` — explicit summary of routes/pages, CSR/SSR/hydrate/islands/SSG posture, and page-load assumptions actually exercised.
- `web-bundle-brief/v0` — bounded summary of Wasm/JS/CSS/assets/base-path/public-url/compression posture that actually shipped in the lane.
- `browser-capability-brief/v0` — explicit summary of `web-sys` features, JS glue/interop posture, unstable APIs, worker/media/canvas/fetch assumptions, and browser-only requirements.
- `web-split-brief/v0` — summary of browser-vs-server code boundaries, SSR/service attachments, and runtime-setting activation that materially changed behavior.
- `web-consumer-handoff/v0` — what deploy/support/docs/atlas consumers may conclude from the pilot and what remains out of scope.
- `web-readiness-scorecard/v0` — not a fake maturity score; a lane-by-lane checklist showing which truths exist and which remain absent.
- `web-product-pack/v0` — attachable summary pack importing the lane artifacts used in a specific pilot.

## Ranked pilot lanes

### 1) Static CSR + base-path lane
**Why first:** it proves the most universal browser-app claim with the least server orchestration.

**Concrete scope**
- route/page identities,
- CSR posture,
- Trunk or equivalent bundle outputs,
- Wasm/JS/CSS/assets presence,
- base path / public URL / static hosting assumptions,
- checked docs/examples for the static lane.

**Graduation bar**
- the pack can explain how the app loads, what files ship, and what path assumptions are required.

### 2) Browser capability / JS interop lane
**Why second:** once page and bundle truth are real, the next hidden pain is whether the app depends on specific browser APIs or JS glue posture.

**Concrete scope**
- `web-sys` feature posture,
- JS wrapper or snippet usage,
- browser API families used,
- unstable Web API posture when relevant,
- worker/media/canvas/fetch/storage assumptions,
- package-vs-app output distinctions when present.

**Graduation bar**
- a reviewer can tell which browser capabilities were actually required and what part of the output depended on JS glue or package generation.

### 3) SSR + hydration split lane
**Why third:** this is where real Rust web products most often hide target-boundary mistakes.

**Concrete scope**
- server-render path versus browser-hydrate path,
- browser-only API isolation,
- server-only dependency posture,
- route/path and hydration assumptions,
- checked evidence for at least one real SSR/hydration pair.

**Graduation bar**
- the pack can explain what belongs to the browser build, what belongs to the server build, and what assumptions make hydration succeed.

### 4) Full-stack deploy lane
**Why fourth:** shipping a web product means more than producing a bundle directory.

**Concrete scope**
- static versus service versus edge/Wasm deploy posture,
- asset/CDN/origin assumptions,
- preview/prod runtime-setting differences,
- deploy receipts or release attachments,
- route-split or bundle-split posture where relevant,
- package/publication posture if a JS-consumable lane also exists.

**Graduation bar**
- the pack can explain what was actually deployed, where assets came from, and which runtime settings changed the product story.

### 5) Support / docs / consumer lane
**Why fifth:** this is where the stack proves it matters beyond demos.

**Concrete scope**
- browser/runtime floors,
- supported render/deploy modes,
- checked docs/examples,
- deploy/release/support handoffs,
- atlas/editor/assistant summaries importing the same artifacts.

**Graduation bar**
- a support or release consumer can answer what web story is actually supported and what evidence shipped with it.

## What to defer
- a universal Rust frontend standard;
- a giant framework comparison or ranking site;
- a fake “web-ready” score before evidence lanes exist;
- another bundler wrapper pretending build output is the whole contract;
- vague “works in the browser” claims that skip route/base-path, browser API, deploy, and support truth.

## Immediate archive consequences
- Treat **Client App Surface** as the anchor of browser-facing route/render/page truth rather than only generic UI surface.
- Treat **Service Surface** as the SSR/server-function/edge attachment lane instead of letting framework docs silently absorb that boundary.
- Treat **Runtime Settings + Host Package** as the browser-path/origin/interop/package lanes that support must import instead of rediscovering from broken deploys.
- Treat **Distribution Contract + Support Envelope + DocProof** as downstream import lanes that should consume lower-layer web evidence instead of retelling it.
- Add a specific amnesia resistor so later revisions cannot collapse render mode, browser capability, bundle/deploy truth, server/client split truth, and support conclusions into one fake readiness story.

## Read this together with
- `design/web-productization-stack.md`
- `design/client-app-surface-kit.md`
- `design/service-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/host-package-kit.md`
- `design/distribution-contract-stack.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
