# Design: Browser Wasm package default lane (package identity + JS glue + bundler/browser target + browser-test + publication truth)

## Goal
Add the first maintained **browser package / npm-published Wasm** defaults-corpus card so the archive can answer a recurring practical question:
**what should a serious Rust-authored browser-consumed package normalize around right now when the real product is a JS/TS package, not a full app?**

This lane should not replace:
- `design/web-productization-stack.md`;
- `design/browser-web-app-default-lane.md`;
- `design/full-stack-rust-web-product-default-lane.md`;
- or `design/wasm-component-kit.md`.

It should give the web-productization frontier its third maintained answer in one bounded project class.

## Why this note is needed now
The archive already had:
- a browser-first web-app card for **CSR + static-hosted assets**;
- a full-stack web-product card for **SSR/hydration with Rust on both halves**;
- and good abstract web-productization theory.

What it still lacked was the remaining central web question:
**what should a Rust team do when the product surface is an npm package consumed by browser-side JavaScript or TypeScript?**

The current public signals make that omission harder to justify:
- Rust’s March 20, 2026 challenges post still frames ecosystem navigation as a problem of **choice paralysis** and **tacit knowledge**;
- the 2025 State of Rust survey still says online docs are the preferred canonical reference while editor/LLM-mediated workflows rise;
- the `wasm-pack build` docs still say the command exists to create the files needed for JavaScript interop and npm publication, including a wasm binary, JS wrapper, `README`, and `package.json`;
- the `wasm-bindgen` guide still makes bundler versus `--target web` output a real deployment/package boundary rather than a tiny flag detail;
- the old `rustwasm` documentation pages now explicitly say they are no longer maintained at that domain and point to new homes;
- the Rust project’s July 2025 Inside Rust post formally sunset the `rustwasm` organization, transferred `wasm-bindgen` to its own organization, and said other repositories such as `wasm-pack` would be archived or transferred;
- and the maintained `drager/wasm-pack` fork has kept shipping releases, which means the lane is still real but its maintenance story is now part of the lane truth.

Together, those signals say the next worthy move is not another general web essay.
It is a bounded boring default card for **browser-consumed Wasm packages published through an npm-shaped interface**.

## Chosen project class
The first browser-package card should cover:
- Rust libraries whose primary public product surface is an npm package consumed in browser-side JS/TS applications;
- teams willing to generate JS glue and TypeScript declarations deliberately instead of treating them as incidental output;
- bundler-first consumption as the conservative default;
- packages that may expose pure computation, data transforms, validation, rendering/math helpers, or focused browser-API helpers;
- and teams that want a path that can later escalate to a wider package matrix without starting from ad hoc glue.

It should **not** try to cover in one card:
- browser-first web apps;
- full-stack SSR/hydration products;
- Node add-ons where the host is really Node and the ABI is Node-API;
- component-model / WIT packages;
- or one universal npm package that equally optimizes for bundlers, direct browser import, Node, Deno, and workers all at once.

## Default thesis
For this bounded project class, the conservative default should currently be:

**`wasm-bindgen` export surface + `wasm-pack build --target bundler` package generation + explicit npm package identity + browser-focused tests via `wasm-pack test` / `wasm-bindgen-test`.**

Why this is the right first card:
- `wasm-bindgen` remains the central, actively maintained Rust↔JavaScript interop layer.
- `wasm-pack build` still produces the exact package-shaped artifact set this lane needs.
- `bundler` remains the conservative target for npm-distributed browser packages because it aligns with the package manager story and browser-support story better than pretending `--target web` and npm consumption are the same thing.
- `wasm-pack test` still wraps `wasm-bindgen-test-runner` and headless browser execution well enough to keep browser receipts visible.
- The maintenance caveat is explicit: `wasm-pack` is no longer a Rust-project-owned central hub tool, so the lane must preserve a fallback path based on raw `wasm-bindgen` plus explicit package scaffolding.

## Serious alternatives that must stay visible
### 1. Raw `wasm-bindgen` CLI + explicit package scaffolding
This wins when the team wants:
- less wrapper magic;
- direct control of `package.json`, output layout, and build orchestration;
- or lower dependence on the current `wasm-pack` maintenance fork.

### 2. Conservative browser web app
This wins when the real product is a web app bundle, routing shell, and deployable asset set rather than a reusable package.
Do not silently widen the package lane into the app lane, or vice versa.

### 3. Conservative full-stack Rust web product
This wins when Rust should own both browser and server halves.
Do not silently widen npm package publication into SSR/hydration/full-stack productization.

### 4. `napi-rs`
This wins when the host is really Node and the lane needs Node-API/native add-on distribution rather than browser-consumed Wasm packages.

### 5. Wasm component / WIT tooling
This wins when the interop target is a component-model runtime or WIT-described interface rather than the JavaScript/browser ecosystem.

## What the card must keep separate
The maintained card should visibly preserve:
- **Rust crate identity**;
- **npm package identity**;
- **generated JS glue identity**;
- **TypeScript declaration truth**;
- **bundler-target versus direct-browser-target truth**;
- **browser API / `web-sys` surface truth**;
- **browser-test truth**;
- **publication / ownership truth**;
- and **lane judgment** versus package-admission judgment.

## Practical design consequences
A real browser-package default card should:
- normalize around `crate-type = ["cdylib"]` and a narrow exported surface via `#[wasm_bindgen]`;
- prefer `wasm-pack build --target bundler` for the default npm/browser package story;
- keep `--target web` visible as a different consumption contract for direct browser import, not as the same package lane;
- keep generated `.d.ts` files, JS wrapper files, and wasm artifact names visible as part of the public package surface;
- isolate `web-sys` usage to the smallest boundary that truly needs browser APIs;
- keep `wasm-bindgen-test` / browser test posture explicit;
- keep exact npm scope/name decisions explicit;
- and treat publication ownership/security as a two-registry problem whenever the crate is also published on crates.io.

## Non-goals
- picking one Rust tool for every JS/TS interop problem;
- flattening browser apps, full-stack web products, browser packages, and component-model packages into one story;
- pretending `wasm-pack` maintenance concerns do not exist;
- or claiming this lane solves Node ABI, edge-worker, or component-model packaging.

## Archive implications
- Add a first maintained browser-package card under `defaults/`.
- Add a first renewal receipt under `evidence/`.
- Refresh corpus/frontier/meta files so the repo now treats **browser-first public web app**, **full-stack Rust web product**, and **browser-consumed Wasm package** as three maintained web lanes.
- After this split, return the corpus to renewal-first discipline rather than widening indefinitely.

## References
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Sunsetting the `rustwasm` organization:
  https://blog.rust-lang.org/inside-rust/2025/07/21/sunsetting-the-rustwasm-github-org/
- `wasm-pack` docs / build / tutorials:
  https://rustwasm.github.io/docs/wasm-pack/introduction.html
  https://rustwasm.github.io/docs/wasm-pack/commands/build.html
  https://rustwasm.github.io/docs/wasm-pack/commands/test.html
  https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/index.html
  https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/packaging-and-publishing.html
- current `wasm-pack` repository / releases:
  https://github.com/drager/wasm-pack
  https://github.com/drager/wasm-pack/releases
- `wasm-bindgen` guide:
  https://rustwasm.github.io/docs/wasm-bindgen/
  https://rustwasm.github.io/docs/wasm-bindgen/reference/deployment.html
  https://rustwasm.github.io/docs/wasm-bindgen/reference/browser-support.html
  https://rustwasm.github.io/docs/wasm-bindgen/reference/js-snippets.html
  https://rustwasm.github.io/docs/wasm-bindgen/reference/cli.html
  https://rustwasm.github.io/docs/wasm-bindgen/wasm-bindgen-test/index.html
  https://rustwasm.github.io/docs/wasm-bindgen/wasm-bindgen-test/browsers.html
- current `wasm-bindgen` repository:
  https://github.com/wasm-bindgen/wasm-bindgen
  https://github.com/wasm-bindgen/wasm-bindgen/releases
- crates.io development update / trusted publishing:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://crates.io/docs/trusted-publishing
