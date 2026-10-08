# Gap: browser-consumed Wasm packages need package-boundary, JS-glue, browser-target, and maintenance truth

## The gap
The archive had:
- browser-first web-app guidance;
- full-stack web-product guidance;
- and broader web-productization theory.

It still lacked a maintained answer for **browser-consumed Wasm packages published through an npm-shaped interface**.

That gap causes predictable confusion:
- teams flatten reusable packages and deployable apps into one vague “Rust web” question;
- `wasm-bindgen` and `wasm-pack` get treated as interchangeable instead of distinct layers;
- generated JS glue and TypeScript declarations get treated as build trivia instead of public surface;
- `--target bundler` and `--target web` get collapsed into one “browser” story;
- and ownership/maintenance truth for `wasm-pack` stays tacit even though the old `rustwasm` home was sunset.

## Why this matters
Current sources now make the split hard to ignore:
- `wasm-pack build` still explicitly creates the JS-interoperable/npm-publication package output;
- the `wasm-bindgen` guide still treats deployment target choice and browser-support behavior as real compatibility decisions;
- the `wasm-bindgen` test docs still distinguish Node, browser, worker, and browser-selection paths;
- the Rust project formally sunset the `rustwasm` organization and transferred only `wasm-bindgen` to a new home;
- the current `wasm-pack` line now lives under `drager/wasm-pack` with ongoing releases;
- and crates.io now exposes more review/security surfaces, which makes exact identity and publication posture more rather than less important.

So the missing contribution is not “another Wasm framework comparison.”
It is a maintained defaults-corpus card that keeps the right truths separate.

## Truths this lane must preserve
- **crate identity truth:** the Rust crate is not the whole public product;
- **npm package truth:** npm naming/scope and package ownership are first-class;
- **generated JS glue truth:** wrapper JS and `.d.ts` files are part of the public contract;
- **browser-target truth:** bundler-first npm consumption is not the same as direct browser `--target web` import;
- **browser-test truth:** headless browser execution is not the same thing as Node-only test success;
- **maintenance truth:** `wasm-bindgen` and `wasm-pack` no longer share the old Rust-project-owned home and should not be narrated as if they do;
- **support/docs truth:** maintained docs and historical docs need to be distinguished explicitly.

## What a good contribution would look like
A worthy contribution here would:
- publish one conservative default for one recurring package class;
- keep raw `wasm-bindgen`, browser-app lanes, `napi-rs`, and component-model lanes visible as alternatives;
- keep bundler-target and direct-browser-target truth separate;
- keep maintenance caveats visible instead of pretending the toolchain story is institutionally settled;
- and attach a renewal receipt that records why the lane still reads the way it does.

## Anti-patterns to avoid
- treating “Rust + Wasm + browser” as one lane;
- letting `wasm-pack` hide crate/package/glue distinctions;
- pretending npm publication and app deployment are the same thing;
- or narrating archived `rustwasm` repositories as if they were still the current maintenance center.
