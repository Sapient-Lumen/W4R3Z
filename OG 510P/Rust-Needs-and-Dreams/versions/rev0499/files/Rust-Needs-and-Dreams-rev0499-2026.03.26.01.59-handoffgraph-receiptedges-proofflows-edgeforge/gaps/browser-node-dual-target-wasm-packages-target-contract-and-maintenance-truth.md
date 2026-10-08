# Gap: browser + Node dual-target Wasm packages still lack target-contract, glue-matrix, and maintenance truth

## The gap
The archive has a maintained **browser Wasm package** lane.
It does not yet have an honest answer for packages that want **both browser and Node** support while remaining JavaScript/Wasm-first.

That omission causes predictable failure modes:
- packages claim “works in JS” without saying which hosts are actually tested;
- browser and Node target differences get hidden behind one build command;
- generated glue gets treated as build trivia rather than public contract;
- target-specific feature asymmetries (for example `js-snippets`) get buried;
- and the post-`rustwasm` maintenance/fallback story stays tacit.

## Why this matters now
The current sources make the split concrete:
- `wasm-pack` explicitly exposes target modes rather than one universal JS target;
- `wasm-bindgen` deployment docs distinguish browser and Node output contracts;
- `js-snippets` support is explicitly limited to `web` and bundler output;
- Node considerations still require caveats about Web APIs such as `fetch`;
- and the Rust project formally sunset the `rustwasm` organization, moving the maintenance story into the foreground.

So the missing contribution is not another generic Rust/Wasm comparison page.
It is a bounded overlay that preserves the right truths.

## Truths the overlay must preserve
- **package-family identity truth** — crate identity, npm identity, and whether there is one package or a deliberate family;
- **target-contract truth** — bundler/browser, direct-browser `web`, Node `nodejs`, and any experimental Node ESM paths are not interchangeable;
- **generated-glue truth** — target-specific wrappers and `.d.ts` files are public surface;
- **runtime-environment truth** — browser APIs, Node APIs, polyfills, and module-loader assumptions must stay explicit;
- **test-matrix truth** — browser evidence and Node evidence are different receipts;
- **maintenance/fallback truth** — convenience tools, raw `wasm-bindgen`, and future component-model paths must stay visibly distinct.

## What a good contribution would look like
A worthy contribution would:
- publish a target/capability/test/release matrix for this package class;
- keep browser-only packages, Node add-ons, worker lanes, and component-model lanes visible as alternatives;
- make it easy to say “split this into narrower lanes” when the unified story is not honest;
- and refuse the common anti-pattern where one README sentence silently becomes the whole compatibility contract.

## Anti-patterns to avoid
- treating browser and Node as “just two test environments” for the same package truth;
- letting one generated glue file stand in for the whole public contract;
- widening this lane into every JS runtime at once;
- or narrating convenience tooling as if the maintenance story were settled and uniform.
