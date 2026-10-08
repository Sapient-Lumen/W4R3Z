# Renewal receipt: conservative browser Wasm package (2026-03-22)

## Subject
- default card: `defaults/conservative-browser-wasm-package-2026Q1.md`
- review date: 2026-03-22
- archive revision: rev0387
- scope: conservative browser-consumed Wasm package published through an npm-shaped interface
- non-goal: package-admission or security signoff for a production package published to npm and/or crates.io

## Renewal verdict
**keep with caveats**

The lane currently still reads best as:
- **`wasm-bindgen`** for the JS/TS export layer,
- **`wasm-pack build --target bundler`** for the current conservative package generator,
- **generated JS wrapper + generated `.d.ts` + `.wasm`** as the visible package surface,
- and **browser-focused tests** via `wasm-pack test` / `wasm-bindgen-test`,

with **raw `wasm-bindgen` + explicit package scaffolding**, **browser-web app lanes**, **`napi-rs`**, and **Wasm component / WIT tooling** kept visible as serious alternatives.

The caveat is important:
this is a **coherent default for browser-consumed npm-shaped Wasm packages**, not a universal answer for browser apps, full-stack web products, Node add-ons, edge workers, or component-model packages.

## Canon import checked this round
Primary documentation surfaces re-read:
- `wasm-pack` build / test / npm tutorial / packaging:
  https://rustwasm.github.io/docs/wasm-pack/commands/build.html
  https://rustwasm.github.io/docs/wasm-pack/commands/test.html
  https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/index.html
  https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/packaging-and-publishing.html
- `wasm-bindgen` introduction / deployment / browser support / CLI / JS snippets / test docs:
  https://rustwasm.github.io/docs/wasm-bindgen/
  https://rustwasm.github.io/docs/wasm-bindgen/reference/deployment.html
  https://rustwasm.github.io/docs/wasm-bindgen/reference/browser-support.html
  https://rustwasm.github.io/docs/wasm-bindgen/reference/cli.html
  https://rustwasm.github.io/docs/wasm-bindgen/reference/js-snippets.html
  https://rustwasm.github.io/docs/wasm-bindgen/wasm-bindgen-test/index.html
  https://rustwasm.github.io/docs/wasm-bindgen/wasm-bindgen-test/browsers.html
- `wasm-pack` current repository / releases:
  https://github.com/drager/wasm-pack
  https://github.com/drager/wasm-pack/releases
- `wasm-bindgen` current repository / activity:
  https://github.com/wasm-bindgen/wasm-bindgen
  https://github.com/wasm-bindgen/wasm-bindgen/releases

Canon judgment:
- `wasm-bindgen` still provides the clearest active JS/TS interop layer for this lane.
- `wasm-pack build` still directly models the package-shaped output this lane needs.
- the package target split is still real: `bundler` is the boring npm/browser package choice, while `web` is a different direct-browser-import contract.
- browser-test posture is still explicit enough to support the lane.
- the maintenance story around `wasm-pack` is now part of the lane truth, not external trivia.

## Registry / supply-chain import
Public ecosystem signals checked:
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io trusted publishing docs:
  https://crates.io/docs/trusted-publishing
- RustSec advisories:
  https://rustsec.org/advisories/

What this receipt takes from those sources:
- if the Rust crate is also published on crates.io, its publication/security posture can now use stronger trusted-publishing controls;
- current crates.io review surfaces are useful for crate-level review but do not solve npm/package ownership or JS-glue review by themselves;
- exact identity matters twice here: once for the Rust crate and once for the npm package.

Exact identity notes for this lane:
- `wasm-bindgen` and `wasm-pack` should be recorded by exact name.
- the Rust crate name and npm package name/scope should be recorded separately.
- this receipt is **not** making claims about a vague bucket called “Rust Wasm tooling”.

Registry judgment:
- the lane remains publishable as a public default card;
- but real package teams still need explicit package-admission, advisory, and multi-registry review on top of it.

## API / compatibility import
Relevant current signals:
- `wasm-pack build` target table and artifact outputs:
  https://rustwasm.github.io/docs/wasm-pack/commands/build.html
- `wasm-bindgen` deployment and supported browsers:
  https://rustwasm.github.io/docs/wasm-bindgen/reference/deployment.html
  https://rustwasm.github.io/docs/wasm-bindgen/reference/browser-support.html
- `wasm-bindgen` CLI TypeScript output and JS-snippet limits:
  https://rustwasm.github.io/docs/wasm-bindgen/reference/cli.html
  https://rustwasm.github.io/docs/wasm-bindgen/reference/js-snippets.html

Judgment:
- this lane still needs visible **target-contract** discipline;
- `bundler` remains the right boring choice because direct-browser `web` output is a different consumption model;
- TypeScript declarations remain part of the public package contract rather than an optional afterthought;
- JS snippets and browser support behavior reinforce that not every target mode carries the same interop guarantees.

## Maintenance / support-envelope import
Envelope facts that still hold:
- package consumers experience the JS wrapper, `.d.ts`, and `.wasm` output as the real product surface;
- browser test posture is real support work, not optional garnish;
- broad browser API exposure via `web-sys` should stay bounded;
- and package publication/security/ownership truth spans more than one registry when crates.io and npm are both involved.

Imported lane-specific warning:
- the old `rustwasm` docs now explicitly say they are no longer maintained at that domain and point to new homes.
- the Rust project’s July 2025 post said `wasm-bindgen` would move to a new organization while repositories such as `wasm-pack` would be archived or transferred.
- the current `drager/wasm-pack` release line still exists and `v0.14.0` on 2026-01-20 added features and maintenance/security fixes, but this is a different maintenance story from pretending `wasm-pack` is still a Rust-project-owned central tool.

Maintenance judgment:
- the lane should stay public;
- but the caveat around `wasm-pack` should stay attached to every renewal.

## Freshness / replay notes
Fresh inputs checked on 2026-03-22:
- Rust challenges post:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- rustwasm sunset / maintenance transition:
  https://blog.rust-lang.org/inside-rust/2025/07/21/sunsetting-the-rustwasm-github-org/
- `drager/wasm-pack` repository / releases:
  https://github.com/drager/wasm-pack
  https://github.com/drager/wasm-pack/releases
- `wasm-bindgen` repository / releases:
  https://github.com/wasm-bindgen/wasm-bindgen
  https://github.com/wasm-bindgen/wasm-bindgen/releases

Replay notes:
- future renewal should explicitly re-check whether `wasm-pack` still deserves to remain the convenience default or whether raw `wasm-bindgen` should replace it;
- re-check whether bundler-first remains the right boring target for npm/browser packages;
- re-check whether browser-package, browser-app, full-stack-web, Node-addon, and component-model lanes are still well-separated;
- re-check whether publication-security or provenance overlays now need to become explicit companion notes.

## Lane judgment
Keep the lane, but keep the maintenance caveat loud.

Why:
- Rust’s official ecosystem framing still says navigation is blocked by tacit knowledge and choice paralysis;
- the current docs now expose package-generation, target, browser-support, and browser-test truths clearly enough that the archive should preserve them;
- and the best public contribution here is still a bounded default with receipts, not a universal blessing.

## Open watch items
- whether a distinct **raw `wasm-bindgen` + explicit package scaffold** discipline should replace `wasm-pack` as the boring default;
- whether a distinct **direct-browser ES-module package** card deserves to split away next;
- whether a **dual browser + Node package** overlay becomes recurring enough to maintain;
- and whether **worker / edge-runtime** package lanes become central enough to justify a separate card.
