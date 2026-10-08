# Renewal receipt: conservative browser web app (2026-03-22)

## Subject
- default card: `defaults/conservative-browser-web-app-2026Q1.md`
- review date: 2026-03-22
- archive revision: rev0385
- scope: browser-first Rust web apps deployed as static assets where the clearest boring default matters more than full-stack maximalism
- non-goal: blessing one Rust web framework for all browser apps, full-stack apps, and Wasm packages

## Renewal verdict
**add as new card**

The defaults corpus still lacked a maintained public web-app card even though the archive already had a strong `design/web-productization-stack.md` theory layer.
The correct first bounded answer for this scope is currently:
- **Leptos in CSR mode** as the framework posture,
- **Trunk** as the bundler/static-asset lane,
- explicit browser capability / interop boundaries,
- explicit bundle/base-path/deploy posture,
- and early escalation to Leptos SSR, Dioxus, Yew, or `wasm-pack` only when the subject is no longer this same lane.

## Canon import checked this round
Primary surfaces re-read:
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
  https://book.leptos.dev/view/index.html
  https://book.leptos.dev/deployment/index.html
  https://book.leptos.dev/deployment/csr.html
  https://book.leptos.dev/deployment/ssr.html
  https://book.leptos.dev/ssr/21_cargo_leptos.html
  https://book.leptos.dev/ssr/22_life_cycle.html
  https://book.leptos.dev/ssr/24_hydration_bugs.html
  https://book.leptos.dev/islands.html
- Dioxus:
  https://dioxuslabs.com/learn/0.7/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
- Yew SSR:
  https://yew.rs/docs/advanced-topics/server-side-rendering
- wasm-bindgen:
  https://rustwasm.github.io/docs/wasm-bindgen/
- wasm-pack:
  https://rustwasm.github.io/docs/wasm-pack/introduction.html
  https://rustwasm.github.io/docs/wasm-pack/commands/build.html
  https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/index.html

Canon judgment:
- browser-facing Wasm is important enough to deserve its own maintained public card;
- Trunk gives the clearest boring bundling/deploy contract for this bounded static-hosted lane;
- Leptos gives the clearest current progression path because its docs explicitly separate CSR from SSR/full-stack and document both deployment and hydration pitfalls;
- Dioxus is a serious alternative, but its own docs keep full-stack/server-client split and multi-surface ambitions visible, so it is better treated as a serious alternative than the default for this narrower scope;
- Yew remains a serious frontend alternative, and its SSR docs are useful evidence that browser APIs and server rendering must stay visibly separate;
- `wasm-bindgen` / `wasm-pack` still point to a different product shape when the subject is primarily a package or JS interop lane.

## Bundle / capability import
Imported judgments:
- a browser web-app card must keep **render mode**, **bundle/base-path posture**, and **browser capability/interop posture** visibly separate;
- Trunk’s HTML-entrypoint plus `dist/` output makes deployable artifact truth clearer than a pile of ad hoc scripts;
- Leptos CSR is a good boring default precisely because it does not hide the tradeoffs: generated JS exists, static hosting is straightforward, and deeper browser capability work should remain explicit rather than ambient.

## Service-boundary / split import
Imported judgments:
- this first card should stay browser-first rather than silently becoming a full-stack Rust web verdict;
- Leptos’s current docs are especially useful because they clearly show the separate SSR/`cargo-leptos` lane, which means escalation paths are explicit rather than hidden;
- Dioxus’s server/client split docs reinforce that “full-stack” is a different lane with a different dependency and binary structure contract.

## Support-envelope / docs import
Imported judgments:
- docs are strong enough now that the lane can be maintained responsibly without pretending the ecosystem has one winner;
- support claims for this lane should stay narrow: browser-first, static-hosted, explicit base-path/deploy posture, explicit service/API boundary;
- the card should not over-claim on SSR, edge, or npm/package lanes.

## Maintenance / queue import
Maintenance judgment:
- this card is central enough to justify widening the corpus again after receipt-complete coverage was achieved;
- but it should remain tightly scoped so later revisions can still add a separate **full-stack Rust web product** card or **browser package / npm-published Wasm** card without rewriting history.

## Freshness / replay notes
Fresh inputs checked on 2026-03-22:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://trunkrs.dev/
- https://book.leptos.dev/getting_started/index.html
- https://book.leptos.dev/deployment/csr.html
- https://book.leptos.dev/deployment/ssr.html
- https://book.leptos.dev/ssr/21_cargo_leptos.html
- https://book.leptos.dev/ssr/24_hydration_bugs.html
- https://book.leptos.dev/islands.html
- https://dioxuslabs.com/learn/0.7/
- https://dioxuslabs.com/learn/0.7/essentials/fullstack/
- https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
- https://yew.rs/docs/advanced-topics/server-side-rendering
- https://rustwasm.github.io/docs/wasm-bindgen/
- https://rustwasm.github.io/docs/wasm-pack/introduction.html
- https://rustwasm.github.io/docs/wasm-pack/commands/build.html

Replay notes:
- renew when Leptos’s browser-first guidance or Trunk’s bundling/deploy posture changes materially;
- renew when Dioxus or another alternative becomes the clearer boring default for this exact scope;
- split the lane when full-stack Rust web products or browser-package products need their own maintained cards;
- keep render mode, package-vs-app identity, and service-boundary truth explicit in every future renewal.

## Lane judgment
Add the card as a maintained public default.

Why:
- it turns a strategically strong web-productization theory layer into a concrete current answer;
- it covers a mainstream Rust product lane rather than an edge case;
- and it does so without pretending browser-first app, full-stack app, and browser-package lanes are already one settled story.

## Open watch items
- whether a separate **full-stack Rust web product** card now deserves to split away from the browser-first lane;
- whether a distinct **browser package / npm-published Wasm** card now deserves to split away from app deployment;
- whether Dioxus’s current web/full-stack story should move upward for this exact scope;
- whether worker/edge/browser-capability-heavy lanes deserve separate treatment rather than implicit widening.
