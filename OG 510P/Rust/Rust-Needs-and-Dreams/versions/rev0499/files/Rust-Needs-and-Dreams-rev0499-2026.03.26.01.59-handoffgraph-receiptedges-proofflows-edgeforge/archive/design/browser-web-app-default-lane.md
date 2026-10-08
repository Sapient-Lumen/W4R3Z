# Design: Browser web app default lane (render mode + bundle/base-path + browser capability + service-boundary truth)

## Goal
Add the first maintained **web-product defaults-corpus card** so the archive can answer a recurring practical question:
**what should a serious browser-first Rust web app normalize around right now if we want the clearest boring default?**

This lane should not replace the broader `design/web-productization-stack.md`.
It should give that stack a first maintained answer in one bounded project class.

## Why this note is needed now
The archive already had a strong web-productization theory layer, but it still lacked a maintained card that said what to actually start with today.
The current public signals make that omission harder to justify:
- Rust’s March 20, 2026 challenges post still frames ecosystem navigation as a problem of **choice paralysis** and **tacit knowledge**;
- the 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated workflows rise;
- the 2024 State of Rust survey says WebAssembly use is mostly in the **browser** (23%) rather than other Wasm contexts (7%), which means browser-facing Wasm is a mainstream Rust lane rather than a side experiment;
- Leptos now documents a clear split between **CSR with Trunk** and **SSR/full-stack with `cargo-leptos`** instead of pretending one mode covers every product;
- Trunk exposes a real HTML-entrypoint → bundle → `dist/` story for Rust web apps instead of leaving asset and loader truth scattered across ad hoc scripts;
- Dioxus and Yew remain credible enough that a useful default has to keep serious alternatives visible rather than pretending the web ecosystem has already converged;
- and `wasm-bindgen` / `wasm-pack` still make plain that **browser package / JS interop** is a different lane from **browser app productization**.

Together, those signals say the next worthy move is **not** another framework comparison chart or web-productization essay.
It is a bounded boring default card.

## Chosen project class
The first web card should cover:
- browser-first Rust web apps rendered in the browser;
- static hosting or CDN-style deployment of built assets;
- products that may talk to an API, but do **not** require Rust-owned SSR as the default assumption;
- teams that want the simplest honest route from Rust UI code to deployable browser assets.

It should **not** try to cover in one card:
- full-stack SSR/hydration products;
- npm-published Wasm packages consumed primarily from JavaScript;
- edge-worker/serverless product lanes;
- cross-platform one-codebase app ambitions spanning web + desktop + mobile;
- or raw browser-capability/interop-heavy libraries.

## Default thesis
For this bounded project class, the conservative default should currently be:

**Leptos in CSR mode + Trunk**, with explicit render-mode choice, explicit browser-capability/interop boundaries, explicit base-path/deploy posture, and a deliberately separate service/API boundary.

Why this is the right first card:
- Leptos’s current book explicitly introduces **CSR with Trunk** as the browser-first path and treats **SSR with `cargo-leptos`** as a separate later lane.
- Trunk gives the clearest boring bundling contract for Rust web apps built around an HTML entrypoint, Wasm output, JS loader, and static asset set.
- Leptos also gives the clearest built-in escalation path when the product later needs SSR, hydration, islands, or tighter server integration.
- This lane stays honest about the normal browser-Wasm tradeoffs: JS bootstrapping exists, initial-load/SEO tradeoffs exist, and base-path/deploy details are product truth.

## Serious alternatives that must stay visible
### 1. Leptos SSR / full-stack with `cargo-leptos`
This wins when Rust should own both the browser and server halves and SEO / initial-load / hydration behavior are central.
It should stay a **separate future card**, not an implicit widening of the CSR card.

### 2. Dioxus web / full-stack
This wins when the team wants a more unified app framework that can span web, desktop, and mobile, and accepts that full-stack/server-client split plus route bundle/deploy posture are part of the framework choice.

### 3. Yew
This wins when the team wants a frontend-focused Rust component model and does not need this card’s chosen framework path.
Yew’s SSR docs remain useful evidence that server-render and browser-API assumptions must stay visibly separate.

### 4. `wasm-pack` / raw `wasm-bindgen`
This wins when the subject is actually a **browser-consumed Wasm package** or a JS-interop-heavy library, not a browser app product.

## What the card must keep separate
The maintained card should visibly preserve:
- **render-mode truth** (`csr` here, not silent future SSR assumptions);
- **bundle/base-path/deploy truth**;
- **browser capability / JS-interop truth**;
- **service/API boundary truth**;
- **support/docs truth**;
- and **lane judgment** versus project-specific escalation.

## Non-goals
- picking one Rust web framework for every web project;
- flattening browser app, full-stack app, and browser-package lanes into one story;
- pretending CSR avoids tradeoffs around SEO, initial load, or JS availability;
- or turning the corpus into a frontend framework scoreboard.

## Archive implications
- Add a first maintained browser-web card under `defaults/`.
- Add a first renewal receipt under `evidence/`.
- Refresh corpus/frontier/meta files so the repo treats **browser-first web app** as a maintained public lane distinct from both **desktop app product** and the broader **web productization stack**.
- Keep a future **full-stack Rust web product** card available as a likely follow-on if the evidence warrants it.

## References
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- 2024 State of Rust survey:
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- Trunk:
  https://trunkrs.dev/
- Leptos book / getting started / deployment:
  https://book.leptos.dev/
  https://book.leptos.dev/getting_started/index.html
  https://book.leptos.dev/deployment/csr.html
  https://book.leptos.dev/deployment/ssr.html
  https://book.leptos.dev/islands.html
  https://book.leptos.dev/ssr/24_hydration_bugs.html
  https://book.leptos.dev/ssr/21_cargo_leptos.html
- Dioxus web/full-stack:
  https://dioxuslabs.com/learn/0.7/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
- Yew SSR:
  https://yew.rs/docs/advanced-topics/server-side-rendering
- wasm-bindgen / wasm-pack:
  https://rustwasm.github.io/docs/wasm-bindgen/
  https://rustwasm.github.io/docs/wasm-pack/introduction.html
  https://rustwasm.github.io/docs/wasm-pack/commands/build.html
