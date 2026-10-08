# Default card: Conservative browser Wasm package (2026 Q1)

Latest renewal receipt: `evidence/conservative-browser-wasm-package-2026Q1-renewal-2026-03-22.md`

## Scope
This card applies to:
- Rust libraries whose primary public product surface is an npm package consumed in browser-side JavaScript or TypeScript applications;
- teams that want a boring bundler-first package lane rather than a deployable app/framework decision;
- packages that expose a focused JS/TS-friendly surface through generated JS glue and TypeScript declarations;
- teams willing to keep browser API usage and JS interop boundaries explicit.

Assumptions:
- stable Rust;
- `wasm32-unknown-unknown` target;
- JS/TS consumers are expected;
- bundler-based consumption is acceptable as the conservative default;
- browser tests are part of the support posture;
- exact crate and npm package identities will be recorded deliberately.

This is **not** the default for:
- browser-first web apps;
- full-stack Rust web products;
- Node add-ons where the host is really Node and the ABI is Node-API;
- component-model / WIT packages;
- or one universal package that equally optimizes for direct browser import, Node, workers, Deno, and bundlers at once.

## Why this default now
Rust’s latest challenges framing still says ecosystem navigation is burdened by **choice paralysis** and **tacit knowledge**.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated workflows rise.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

The `wasm-pack build` docs still say the command creates the files necessary for JavaScript interoperability and publishing a package to npm, including the wasm binary, JS wrapper, `README`, and `package.json`.
https://rustwasm.github.io/docs/wasm-pack/commands/build.html

Those same docs make the package-target split explicit:
- default / `bundler` output is for bundlers and records the `module` key in `package.json`;
- `web` output is for native browser ES-module import and manual wasm loading;
- and `no-modules` is older browser-global output with fewer features.
https://rustwasm.github.io/docs/wasm-pack/commands/build.html
https://rustwasm.github.io/docs/wasm-bindgen/reference/deployment.html

The `wasm-bindgen` guide still says browser support is strongest when using a bundler or `--target web`, and its CLI still generates TypeScript declarations by default.
https://rustwasm.github.io/docs/wasm-bindgen/reference/browser-support.html
https://rustwasm.github.io/docs/wasm-bindgen/reference/cli.html

Browser-test posture is also still explicit: `wasm-pack test` wraps `wasm-bindgen-test-runner`, supports browser flags, and headless execution is part of the documented CI path.
https://rustwasm.github.io/docs/wasm-pack/commands/test.html
https://rustwasm.github.io/docs/wasm-bindgen/wasm-bindgen-test/browsers.html

The maintenance caveat is real and belongs in the default:
- the Rust project formally sunset the `rustwasm` organization in 2025;
- the old docs now explicitly say they are no longer maintained at that domain and point to new homes;
- `wasm-bindgen` moved to its own actively maintained organization;
- and `wasm-pack` now lives in the maintained `drager/wasm-pack` fork with a January 20, 2026 `v0.14.0` release.
https://blog.rust-lang.org/inside-rust/2025/07/21/sunsetting-the-rustwasm-github-org/
https://github.com/wasm-bindgen/wasm-bindgen
https://github.com/drager/wasm-pack
https://github.com/drager/wasm-pack/releases

For this exact project class, the archive’s current answer is:
**use `wasm-bindgen` for the exported JS/TS surface, use `wasm-pack build --target bundler` as the current conservative package generator, keep npm package identity explicit, keep browser tests explicit, and keep raw `wasm-bindgen` + explicit package scaffolding visible as the fallback when tighter control or lower wrapper dependence matters.**

## Decision label
**default-with-caveats**

It is the clearest boring default for this narrow package scope, but the maintenance story around `wasm-pack` means the caveat must stay loud.

## Default lane summary
### Default lane
- export / glue layer: **`wasm-bindgen`**
- package generator: **`wasm-pack`**
- target posture: **`wasm-pack build --target bundler`**
- package surface: **generated JS wrapper + generated `.d.ts` + `.wasm` + explicit npm package identity**
- browser API posture: **prefer pure/browser-agnostic exports first; isolate `web-sys` to the smallest boundary that truly needs browser APIs**
- test posture: **browser-focused tests via `wasm-pack test` / `wasm-bindgen-test` with headless browsers in CI**
- publication posture: **keep crate identity and npm package identity both explicit; do not assume one registry name explains the other**

### Serious alternatives
- **raw `wasm-bindgen` CLI + explicit package scaffolding** when the team wants tighter control of package layout, tooling, and generated artifacts.
- **conservative browser web app** when the real product is a browser app bundle and deployment story, not a reusable package.
- **conservative full-stack Rust web product** when Rust should own both browser and server halves.
- **`napi-rs`** when the true host is Node rather than the browser.
- **Wasm component / WIT tooling** when the interop target is a component-model runtime rather than JavaScript/browser consumers.

### Watch / not-default here
- **direct-browser `--target web` publication** as a distinct consumption contract rather than a silent variant of the bundler/npm lane.
- **browser + Node dual-target packages** as a future overlay rather than the boring default.
- **worker-first / edge-runtime packages** as a future narrower lane rather than a silent widening of browser package guidance.

## Slot guidance
### Package-identity slot
Record **both** the Rust crate name and the npm package name/scope explicitly.
Do not pretend one automatically explains the other.

### Export / glue slot
Keep `#[wasm_bindgen]` exports narrow and deliberate.
Treat the generated JS wrapper and `.d.ts` files as part of the public package contract, not as invisible build byproducts.

### Target / consumer slot
Prefer **`bundler`** as the conservative target for npm/browser packages.
Do not silently drift from bundler-based npm consumption into direct browser `--target web` guidance.

### Browser-API slot
Prefer pure or browser-agnostic exports first.
If browser APIs are necessary, isolate `web-sys` and handwritten JS interop to the smallest boundary that needs them.
Do not let one browser API demo silently become the package’s whole portability story.

### Test slot
Keep browser tests explicit.
Node-only success is not enough evidence for a browser-consumed package.
Use headless browser execution in CI when the support promise includes browsers.

### Publication / support slot
Keep publication ownership, package scope, changelog/readme/docs expectations, and security posture explicit.
If the crate is also published on crates.io, keep the two registry identities and release mechanics distinct.

## Serious alternatives and when they win
### Raw `wasm-bindgen` CLI wins when
- the team wants less wrapper tooling;
- package layout and JS glue handling need tighter explicit control;
- or the `wasm-pack` maintenance caveat is heavy enough that a thinner toolchain is preferable.

### Browser-web app lanes win when
- the real product is a deployed app shell, route tree, and asset bundle;
- framework/render-mode/deploy posture matter more than reusable package publication;
- or the package is really just one implementation detail of a broader app.

### `napi-rs` wins when
- the host is Node, not the browser;
- Node-API/native add-on distribution is intentional;
- or browser Wasm is only a side requirement.

### Wasm component / WIT lanes win when
- the interop contract is not JS-first;
- the target is a component runtime or WIT-described interface;
- or package composition matters more than JavaScript glue.

## Escalate to a project-specific brief when
- the package must support both bundlers and direct browser import as equal first-class targets;
- Node and browser support are both mandatory under one package contract;
- worker/service-worker/edge-runtime constraints dominate the design;
- deep browser API surface or large `web-sys` exposure becomes central;
- or the release process needs a stronger multi-registry security/provenance story than this card carries.

## Canonical references
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rustwasm sunset / maintenance transition:
  https://blog.rust-lang.org/inside-rust/2025/07/21/sunsetting-the-rustwasm-github-org/
- `wasm-pack` docs:
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
  https://rustwasm.github.io/docs/wasm-bindgen/reference/cli.html
  https://rustwasm.github.io/docs/wasm-bindgen/reference/deployment.html
  https://rustwasm.github.io/docs/wasm-bindgen/reference/browser-support.html
  https://rustwasm.github.io/docs/wasm-bindgen/reference/js-snippets.html
  https://rustwasm.github.io/docs/wasm-bindgen/wasm-bindgen-test/index.html
  https://rustwasm.github.io/docs/wasm-bindgen/wasm-bindgen-test/browsers.html
- current `wasm-bindgen` repository / releases:
  https://github.com/wasm-bindgen/wasm-bindgen
  https://github.com/wasm-bindgen/wasm-bindgen/releases
- crates.io trusted publishing / development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://crates.io/docs/trusted-publishing

## Renewal inputs
Recheck before renewal:
- whether `wasm-bindgen` remains the clearest active interop layer for this exact package scope;
- whether `wasm-pack` remains viable enough to stay the convenience default or whether raw `wasm-bindgen` should replace it;
- whether `bundler` remains the right boring target for browser/npm packages;
- whether browser-only, full-stack, browser-package, Node-addon, and component-model lanes are still well-separated;
- and whether browser-test or publication-security expectations now require a narrower overlay.

## Open watch items
- whether a stronger **raw `wasm-bindgen` + explicit package scaffold** discipline should replace `wasm-pack` as the boring default;
- whether a distinct **direct-browser ES-module package** card deserves to split from the bundler-first lane;
- whether a **dual browser + Node package** overlay becomes central enough to maintain;
- and whether **edge-runtime / worker-first** package lanes become recurring enough to justify their own card.
