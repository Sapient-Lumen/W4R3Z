# Design: Browser + Node dual-target Wasm package overlay

## Goal
Define the missing overlay above the current **browser Wasm package** card for a recurring but more demanding project class:

**one Rust-authored JS/Wasm package family that deliberately wants both browser and Node consumers to matter.**

This is not the same thing as:
- a browser-only npm package;
- a Node-native add-on (`napi-rs` / Node-API);
- a full app;
- a worker-first edge product;
- or a Wasm Component / WIT package.

It is an overlay because the existing browser-package card remains valid as the boring starting point.
The missing work is to model the extra truth that appears once **browser and Node both become first-class consumers**.

## Why this note is needed now
The current browser-package default card already names this as an unresolved watch item.
Fresh ecosystem signals make the omission harder to ignore:
- the `rustwasm` organization was formally sunset in 2025, which means maintenance and ownership truth can no longer be treated as background trivia;
- `wasm-pack` still exposes a real target matrix (`bundler`, `nodejs`, `web`, `no-modules`, `deno`) rather than one universal JS package target;
- the `wasm-bindgen` deployment docs still distinguish browser `web`, Node `nodejs`, and `experimental-nodejs-module` as separate output contracts;
- `wasm-bindgen`’s `js-snippets` support is explicitly limited to `web` and bundler output, which means important capabilities do not map cleanly across all targets;
- `wasm-pack`’s own Node considerations still document fetch/polyfill caveats;
- and the 2026 Rust goals now put **Wasm Components** on the official roadmap, which raises the cost of pretending today’s JS-target matrix is already a solved universal package lane.
https://blog.rust-lang.org/inside-rust/2025/07/21/sunsetting-the-rustwasm-github-org/
https://rustwasm.github.io/docs/wasm-pack/commands/build.html
https://rustwasm.github.io/docs/wasm-bindgen/reference/deployment.html
https://rustwasm.github.io/docs/wasm-bindgen/reference/js-snippets.html
https://rustwasm.github.io/docs/wasm-pack/prerequisites/considerations.html
https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## The missing question
The archive can already answer:
- what should a **browser-consumed Wasm package** do?
- what should a **browser-first web app** do?
- what should a **full-stack Rust web product** do?

It still cannot answer this sharper question:

**what should a serious Rust package do when one npm/distribution family wants both browser and Node consumers without drifting into native Node add-ons or pretending one glue target works everywhere?**

That gap matters because the hard parts are not “compile to Wasm twice.”
They are:
- package-identity and export-map truth;
- target-specific generated JS glue;
- browser API versus Node API / polyfill truth;
- test-matrix truth;
- maintenance/fallback truth after the `rustwasm` transition;
- and deciding when a unified package is a real product goal versus an attractive nuisance.

## Project class
This overlay should cover:
- Rust-authored libraries distributed through an npm-shaped package family;
- teams that want one shared Rust core with explicit browser and Node target outputs;
- packages where browser and Node are both deliberate support claims rather than accidental side effects;
- packages willing to publish a real compatibility matrix instead of one vague “works in JS” promise.

It should **not** try to cover:
- native Node add-ons where the host is really Node-API;
- worker-first edge runtimes as the main target;
- Wasm Component / WIT packages;
- or every JavaScript platform at once (browser + Node + Deno + Bun + workers + direct ESM + CommonJS + component-model) under one fake universal lane.

## Default thesis for the overlay
The likely conservative answer for this overlay is **not** “one target and hope.”
It is closer to:

**start from the existing browser-package discipline, add Node as an explicit second target/output family, publish a real target-capability matrix, and keep browser-specific and Node-specific escape hatches visible instead of flattening them into one package myth.**

In practice that means a worthy contribution here should normalize around:
- one Rust core crate or workspace subject;
- explicit target-output families (for example, bundler/browser output and Node output);
- explicit `package.json` / export-map / condition truth;
- explicit generated-glue ownership per target;
- explicit browser-test and Node-test posture;
- explicit unsupported-feature / polyfill / snippet / env differences;
- and a fallback path based on raw `wasm-bindgen` plus explicit package scaffolding whenever convenience wrappers stop telling the truth.

## Truths this overlay must preserve
A real design here must keep these distinct:

### 1. Package-family identity truth
- crate identity;
- npm package identity / scope;
- whether one package or multiple packages are being published;
- and whether browser and Node are equal first-class products or one is secondary.

### 2. Target-contract truth
- bundler/browser output;
- direct-browser `web` output;
- Node `nodejs` output;
- any experimental Node ESM posture;
- and which target is actually claimed as stable versus watch/experimental.

### 3. Glue and feature-surface truth
- generated JS wrapper files are target-dependent public surface;
- `.d.ts` files are part of the public contract;
- `js-snippets` support asymmetry must stay visible;
- browser-only APIs and Node-only assumptions must not be narrated as “just JavaScript”.

### 4. Runtime-environment truth
- browser globals / DOM / `web-sys` assumptions;
- Node globals / `fetch` / module-loader assumptions;
- polyfills or shims;
- and any ESM/CommonJS friction.

### 5. Test-matrix truth
- browser CI evidence;
- Node CI evidence;
- what is smoke-tested versus fully supported;
- and whether shared fixtures really prove the same semantics across both hosts.

### 6. Maintenance and fallback truth
- which toolchain pieces are institutionally settled and which are “useful but caveated”;
- when the package lane should fall back to raw `wasm-bindgen` + explicit packaging;
- and when the team should split into two narrower package lanes instead of forcing one overlay.

## What a worthy contribution would look like in theory and practice
A strong ecosystem contribution here would not primarily be another wrapper crate.
It would be a **reviewable overlay contract** above current tools.

Concretely, it should aim for something like:
- `dual-target-jswasm-profile/v0`
- `dual-target-glue-matrix/v0`
- `dual-target-capability-report/v0`
- `dual-target-test-pack/v0`
- `dual-target-release-pack/v0`

Those artifacts should let a reviewer answer:
1. What exact targets are claimed?
2. What generated artifacts belong to each target?
3. Which host APIs or polyfills are assumed?
4. Which tests ran where?
5. Which features are shared, degraded, or unsupported?
6. When should consumers prefer a narrower browser-only or Node-only package instead?

That is the missing strategic layer.
Without it, the ecosystem will keep oscillating between:
- simplistic browser-only guidance;
- Node-only native-addon lanes;
- or under-specified “works in JS” packages.

## Serious alternatives that must stay visible
### 1. Conservative browser Wasm package
This still wins when browser-side consumption is the clear product center of gravity.
Do not promote the overlay just because Node support sounds ambitious.

### 2. `napi-rs`
This wins when Node-native distribution and Node-API integration are the point.
Do not force a Wasm overlay where a Node add-on lane is the honest answer.

### 3. Worker-first / edge-runtime lanes
These win when the true runtime is a managed or self-hosted worker/edge platform rather than ordinary browser + Node consumers.

### 4. Wasm Components / WIT tooling
This wins when the real interop contract is component-model-first rather than JavaScript-first.

### 5. Raw custom Wasmtime embedder
This wins when the host wants to own the runtime directly instead of living inside JS platform contracts.

## Non-goals
- one universal npm package that is equally optimal for every JS runtime;
- hiding target-specific contracts behind one cheerful README sentence;
- pretending `browser + Node` is the same as `browser + worker + Deno + Bun + edge`;
- or claiming today’s JS glue toolchain is already superseded by Wasm Components.

## Recommended archive consequence
- Keep the current **browser Wasm package** card as the boring default for the narrower browser-only lane.
- Treat this overlay as the clearest next public-lane candidate if the archive widens the defaults corpus again.
- Do **not** jump directly to a maintained default card until the overlay can name a real target/capability/test/release matrix rather than just a wish.
- Keep **raw custom Wasmtime embedder** and **durable internal library** behind this overlay in the next-lane queue.

## References
- Sunsetting the `rustwasm` organization:
  https://blog.rust-lang.org/inside-rust/2025/07/21/sunsetting-the-rustwasm-github-org/
- `wasm-pack` build docs:
  https://rustwasm.github.io/docs/wasm-pack/commands/build.html
- `wasm-pack` Node considerations:
  https://rustwasm.github.io/docs/wasm-pack/prerequisites/considerations.html
- `wasm-bindgen` deployment docs:
  https://rustwasm.github.io/docs/wasm-bindgen/reference/deployment.html
- `wasm-bindgen` JS-snippets docs:
  https://rustwasm.github.io/docs/wasm-bindgen/reference/js-snippets.html
- `wasm-bindgen` guide:
  https://rustwasm.github.io/docs/wasm-bindgen/
- Rust in 2026 / Wasm Components:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Wasmtime component embedding docs:
  https://docs.rs/wasmtime/latest/wasmtime/component/index.html
  https://docs.wasmtime.dev/wasip2-plugins.html
