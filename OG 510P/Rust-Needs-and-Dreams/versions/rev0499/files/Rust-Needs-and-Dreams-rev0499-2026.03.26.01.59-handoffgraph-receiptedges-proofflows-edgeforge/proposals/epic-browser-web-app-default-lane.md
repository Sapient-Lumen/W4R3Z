# Epic proposal: Browser web app default lane

## Thesis
Add a maintained defaults-corpus card for **browser-first Rust web apps** so the archive can answer a common practical question with a bounded current recommendation instead of only a broad productization theory.

## Proposed artifact family
- `design/browser-web-app-default-lane.md`
- `defaults/conservative-browser-web-app-2026Q1.md`
- `evidence/conservative-browser-web-app-2026Q1-renewal-2026-03-22.md`
- frontier/meta refresh tying the new card to `design/web-productization-stack.md`

## Initial lane judgment
For the narrow browser-first/static-hosted app scope, publish:
- **Leptos CSR + Trunk** as the conservative default;
- **Leptos SSR/`cargo-leptos`**, **Dioxus**, **Yew**, and **`wasm-pack` / raw `wasm-bindgen`** as serious alternatives for different scopes;
- explicit separation of render mode, bundle/base-path posture, browser capability/interop, service boundary, and docs/support posture.

## Why this is epic-worthy
- It turns an existing frontier stack into a reusable current answer.
- It covers a mainstream Rust product lane rather than an edge case.
- It helps future onramp/default tooling consume a bounded recommendation without pretending to solve all web work at once.

## Non-goals
- declaring one Rust web framework the universal winner;
- collapsing browser-app, full-stack, and browser-package lanes into one card;
- or replacing `design/web-productization-stack.md`.
